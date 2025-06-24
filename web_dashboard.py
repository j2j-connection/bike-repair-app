#!/usr/bin/env python3
"""
Web Dashboard for Strava Traffic Monitor

This creates a web interface to view traffic comparison data
and monitor status from any device on your network.
Now supports OAuth authentication for multiple users.
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash, get_flashed_messages
import sqlite3
from datetime import datetime, timedelta
import json
import os
import secrets
from strava_monitor import StravaMonitor, StoredTrafficComparison
from traffic_comparison import GoogleMapsAPI
import requests

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system environment variables

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Strava OAuth Configuration
STRAVA_CLIENT_ID = os.environ.get('STRAVA_CLIENT_ID', 'your_strava_client_id_here')
STRAVA_CLIENT_SECRET = os.environ.get('STRAVA_CLIENT_SECRET', 'your_strava_client_secret_here')
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'your_google_maps_api_key_here')

# OAuth redirect URI (should match your Strava app settings)
REDIRECT_URI = 'http://localhost:5001/oauth/callback'

def load_config():
    """Load configuration from environment variables or config file."""
    try:
        from config import (
            STRAVA_CLIENT_ID as CONFIG_CLIENT_ID,
            STRAVA_CLIENT_SECRET as CONFIG_CLIENT_SECRET,
            GOOGLE_MAPS_API_KEY as CONFIG_MAPS_KEY
        )
        return (
            STRAVA_CLIENT_ID if STRAVA_CLIENT_ID != 'your_strava_client_id_here' else CONFIG_CLIENT_ID,
            STRAVA_CLIENT_SECRET if STRAVA_CLIENT_SECRET != 'your_strava_client_secret_here' else CONFIG_CLIENT_SECRET,
            GOOGLE_MAPS_API_KEY if GOOGLE_MAPS_API_KEY != 'your_google_maps_api_key_here' else CONFIG_MAPS_KEY
        )
    except ImportError:
        return STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, GOOGLE_MAPS_API_KEY

def get_monitor_for_user(user_id=None):
    """Get monitor instance for a specific user or the default configuration."""
    client_id, client_secret, maps_api_key = load_config()
    
    if not all([client_id, client_secret, maps_api_key]):
        return None
    
    # If user is authenticated, use their access token
    if user_id and 'strava_tokens' in session and user_id in session['strava_tokens']:
        access_token = session['strava_tokens'][user_id]['access_token']
    else:
        # Fall back to default config
        try:
            from config import STRAVA_ACCESS_TOKEN
            access_token = STRAVA_ACCESS_TOKEN
        except ImportError:
            return None
    
    from strava_brake_wear_estimator import StravaAPI
    strava_api = StravaAPI(str(client_id), str(client_secret), str(access_token))
    google_maps_api = GoogleMapsAPI(str(maps_api_key))
    
    return StravaMonitor(strava_api, google_maps_api)

def get_user_athlete_info(user_id):
    """Get athlete information for a user."""
    if 'strava_tokens' not in session or user_id not in session['strava_tokens']:
        return None
    
    access_token = session['strava_tokens'][user_id]['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get("https://www.strava.com/api/v3/athlete", headers=headers)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    return None

@app.route('/')
def dashboard():
    """Main dashboard page."""
    flash_messages = get_flashed_messages(with_categories=True)
    return render_template('dashboard.html', flash_messages=flash_messages)

@app.route('/login')
def login():
    """Redirect to Strava OAuth."""
    client_id, _, _ = load_config()
    if client_id == 'your_strava_client_id_here':
        flash('Strava API not configured. Please set up your Strava app credentials.', 'error')
        return redirect(url_for('dashboard'))
    
    auth_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&response_type=code&redirect_uri={REDIRECT_URI}&approval_prompt=force&scope=activity:read_all"
    return redirect(auth_url)

@app.route('/oauth/callback')
def oauth_callback():
    """Handle OAuth callback from Strava."""
    code = request.args.get('code')
    if not code:
        flash('Authorization failed. Please try again.', 'error')
        return redirect(url_for('dashboard'))
    
    client_id, client_secret, _ = load_config()
    
    # Exchange code for access token
    token_url = "https://www.strava.com/oauth/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code"
    }
    
    try:
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            
            # Get athlete info
            athlete_info = get_athlete_info(token_data['access_token'])
            if athlete_info:
                user_id = str(athlete_info['id'])
                
                # Store tokens in session
                if 'strava_tokens' not in session:
                    session['strava_tokens'] = {}
                
                session['strava_tokens'][user_id] = {
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token', ''),
                    'expires_at': token_data.get('expires_at', 0),
                    'athlete_info': athlete_info
                }
                
                session['current_user_id'] = user_id
                flash(f'Welcome, {athlete_info.get("firstname", "Athlete")}!', 'success')
            else:
                flash('Failed to get athlete information.', 'error')
        else:
            flash('Failed to get access token.', 'error')
    except Exception as e:
        flash(f'Authentication error: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

def get_athlete_info(access_token):
    """Get athlete information using access token."""
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get("https://www.strava.com/api/v3/athlete", headers=headers)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

@app.route('/logout')
def logout():
    """Logout current user."""
    if 'current_user_id' in session:
        user_id = session['current_user_id']
        if 'strava_tokens' in session and user_id in session['strava_tokens']:
            del session['strava_tokens'][user_id]
        del session['current_user_id']
        flash('Logged out successfully.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/api/comparisons')
def get_comparisons():
    """Get all traffic comparisons as JSON."""
    user_id = session.get('current_user_id')
    monitor = get_monitor_for_user(user_id)
    
    if not monitor:
        return jsonify({"error": "Monitor not available. Please log in to Strava."})
    
    comparisons = monitor.get_all_comparisons()
    
    # Convert to JSON-serializable format
    data = []
    for comp in comparisons:
        data.append({
            "id": comp.id,
            "activity_id": comp.activity_id,
            "activity_name": comp.activity_name,
            "ride_date": comp.ride_date,
            "bike_time_minutes": comp.bike_time_minutes,
            "car_time_minutes": comp.car_time_minutes,
            "time_saved_minutes": comp.time_saved_minutes,
            "time_saved_percentage": comp.time_saved_percentage,
            "distance_miles": comp.distance_miles,
            "bike_speed_mph": comp.bike_speed_mph,
            "car_speed_mph": comp.car_speed_mph,
            "traffic_conditions": comp.traffic_conditions,
            "route_summary": comp.route_summary,
            "captured_at": comp.captured_at
        })
    
    return jsonify(data)

@app.route('/api/stats')
def get_stats():
    """Get summary statistics."""
    user_id = session.get('current_user_id')
    monitor = get_monitor_for_user(user_id)
    
    if not monitor:
        return jsonify({"error": "Monitor not available. Please log in to Strava."})
    
    comparisons = monitor.get_all_comparisons()
    
    if not comparisons:
        return jsonify({
            "total_rides": 0,
            "total_distance": 0,
            "total_time_saved": 0,
            "average_time_saved": 0,
            "total_bike_time": 0,
            "total_car_time": 0,
            "average_bike_speed": 0,
            "average_car_speed": 0
        })
    
    total_time_saved = sum(comp.time_saved_minutes for comp in comparisons)
    total_distance = sum(comp.distance_miles for comp in comparisons)
    total_bike_time = sum(comp.bike_time_minutes for comp in comparisons)
    total_car_time = sum(comp.car_time_minutes for comp in comparisons)
    
    stats = {
        "total_rides": len(comparisons),
        "total_distance": round(total_distance, 1),
        "total_time_saved": round(total_time_saved, 1),
        "average_time_saved": round(total_time_saved / len(comparisons), 1),
        "total_bike_time": round(total_bike_time, 1),
        "total_car_time": round(total_car_time, 1),
        "average_bike_speed": round(total_distance / (total_bike_time / 60), 1),
        "average_car_speed": round(total_distance / (total_car_time / 60), 1)
    }
    
    return jsonify(stats)

@app.route('/api/pending')
def get_pending():
    """Get pending captures."""
    user_id = session.get('current_user_id')
    monitor = get_monitor_for_user(user_id)
    
    if not monitor:
        return jsonify({"error": "Monitor not available. Please log in to Strava."})
    
    pending = monitor.get_pending_captures()
    return jsonify(pending)

@app.route('/api/status')
def get_status():
    """Get monitor status."""
    user_id = session.get('current_user_id')
    monitor = get_monitor_for_user(user_id)
    
    if not monitor:
        return jsonify({"error": "Monitor not available. Please log in to Strava."})
    
    # Check internet connection
    is_online = monitor.check_internet_connection()
    
    # Get database info
    conn = sqlite3.connect(monitor.db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM traffic_comparisons')
    total_comparisons = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM pending_captures')
    pending_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT MAX(captured_at) FROM traffic_comparisons')
    last_capture = cursor.fetchone()[0]
    
    conn.close()
    
    # Get user info
    user_info = None
    if user_id and 'strava_tokens' in session and user_id in session['strava_tokens']:
        user_info = session['strava_tokens'][user_id].get('athlete_info', {})
    
    status = {
        "online": is_online,
        "total_comparisons": total_comparisons,
        "pending_captures": pending_count,
        "last_capture": last_capture,
        "last_check": datetime.now().isoformat(),
        "user_info": user_info
    }
    
    return jsonify(status)

@app.route('/api/trigger_check')
def trigger_check():
    """Manually trigger a check for new activities."""
    user_id = session.get('current_user_id')
    monitor = get_monitor_for_user(user_id)
    
    if not monitor:
        return jsonify({"error": "Monitor not available. Please log in to Strava."})
    
    try:
        new_comparisons = monitor.check_for_new_activities()
        return jsonify({
            "success": True,
            "new_comparisons": len(new_comparisons),
            "activities": [comp.activity_name for comp in new_comparisons]
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/user_info')
def get_user_info():
    """Get current user information."""
    user_id = session.get('current_user_id')
    
    if not user_id or 'strava_tokens' not in session or user_id not in session['strava_tokens']:
        return jsonify({"authenticated": False})
    
    user_info = session['strava_tokens'][user_id].get('athlete_info', {})
    return jsonify({
        "authenticated": True,
        "user_info": user_info
    })

if __name__ == '__main__':
    print("🌐 Starting Web Dashboard...")
    print("   Dashboard will be available at: http://localhost:5001")
    print("   On your network: http://[YOUR_MAC_MINI_IP]:5001")
    print("   Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5001, debug=False) 