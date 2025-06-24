#!/usr/bin/env python3
"""
Strava App Setup Helper

This script helps you set up your Strava app credentials for OAuth authentication.
"""

import os
import webbrowser
from pathlib import Path

def main():
    """Main setup function."""
    print("🚴‍♂️ Strava App Setup for OAuth Authentication")
    print("=" * 50)
    print()
    
    print("To enable OAuth authentication for multiple users, you need to:")
    print("1. Create a Strava API application")
    print("2. Configure the redirect URI")
    print("3. Set up environment variables")
    print()
    
    # Step 1: Create Strava API application
    print("📋 Step 1: Create Strava API Application")
    print("-" * 40)
    print("1. Go to https://www.strava.com/settings/api")
    print("2. Fill in the following details:")
    print("   - Application Name: 'Traffic Monitor' (or your preferred name)")
    print("   - Category: 'Analytics'")
    print("   - Website: http://localhost:5000")
    print("   - Authorization Callback Domain: localhost")
    print("3. Click 'Create'")
    print()
    
    create_app = input("Open Strava API settings page? (y/n): ").strip().lower()
    if create_app == 'y':
        webbrowser.open("https://www.strava.com/settings/api")
    
    print()
    print("After creating your app, you'll get:")
    print("- Client ID")
    print("- Client Secret")
    print()
    
    # Step 2: Get credentials
    print("🔑 Step 2: Enter Your App Credentials")
    print("-" * 40)
    
    client_id = input("Enter your Client ID: ").strip()
    client_secret = input("Enter your Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Client ID and Client Secret are required!")
        return
    
    # Step 3: Create .env file
    print()
    print("💾 Step 3: Creating Environment Configuration")
    print("-" * 40)
    
    env_content = f"""# Strava API Configuration
STRAVA_CLIENT_ID={client_id}
STRAVA_CLIENT_SECRET={client_secret}

# Google Maps API Key (required for traffic analysis)
# Get this from https://console.cloud.google.com/
# Enable Directions API for traffic estimation
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Flask Secret Key (auto-generated)
SECRET_KEY={os.urandom(32).hex()}
"""
    
    env_file = Path('.env')
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created {env_file}")
    print()
    
    # Step 4: Update config.py
    print("⚙️ Step 4: Updating Configuration")
    print("-" * 40)
    
    config_content = f"""# Strava API Configuration
# These values are now loaded from environment variables
# See .env file for actual values

# Strava API Credentials
STRAVA_CLIENT_ID = os.environ.get('STRAVA_CLIENT_ID', 'your_strava_client_id_here')
STRAVA_CLIENT_SECRET = os.environ.get('STRAVA_CLIENT_SECRET', 'your_strava_client_secret_here')
STRAVA_ACCESS_TOKEN = "your_strava_access_token_here"  # Fallback for single-user mode

# Google Maps API Key for traffic comparison
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', 'your_google_maps_api_key_here')

# Brake Pad Configuration
BRAKE_MATERIAL = "sintered"  # Options: "organic", "semi-metallic", "ceramic", "sintered"
INITIAL_THICKNESS_MM = 4.0
MINIMUM_THICKNESS_MM = 1.0

# Rider and Bike Configuration
RIDER_WEIGHT_KG = 75.0
BIKE_WEIGHT_KG = 12.0

# Analysis Configuration
DAYS_BACK = 30  # Number of days to analyze
"""
    
    config_file = Path('config.py')
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Updated {config_file}")
    print()
    
    # Step 5: Instructions
    print("🎉 Setup Complete!")
    print("=" * 40)
    print()
    print("Next steps:")
    print("1. Add your Google Maps API key to the .env file")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Run the dashboard: python web_dashboard.py")
    print("4. Visit http://localhost:5000")
    print("5. Click 'Login with Strava' to authenticate")
    print()
    print("Important notes:")
    print("- The .env file contains sensitive information - don't commit it to version control")
    print("- Add .env to your .gitignore file")
    print("- For production, set environment variables on your server")
    print("- The redirect URI is set to http://localhost:5000/oauth/callback")
    print()

if __name__ == "__main__":
    main() 