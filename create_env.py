#!/usr/bin/env python3
"""
Create Environment File

This script helps you create the .env file for OAuth configuration.
"""

import os
from pathlib import Path

def main():
    """Create .env file with user's credentials."""
    print("🔧 Creating .env file for OAuth configuration")
    print("=" * 50)
    
    # Get Client Secret
    print("\n📋 Step 1: Strava App Credentials")
    print("-" * 30)
    print("You have Client ID: 164037")
    client_secret = input("Enter your Client Secret: ").strip()
    
    if not client_secret:
        print("❌ Client Secret is required!")
        return
    
    # Get Google Maps API Key
    print("\n🗺️ Step 2: Google Maps API Key")
    print("-" * 30)
    print("You need a Google Maps API key for traffic analysis.")
    print("Get one from: https://console.cloud.google.com/")
    print("Enable the Directions API for traffic estimation.")
    maps_key = input("Enter your Google Maps API Key: ").strip()
    
    if not maps_key:
        print("⚠️  Google Maps API key is recommended for full functionality")
        maps_key = "your_google_maps_api_key_here"
    
    # Generate secret key
    secret_key = os.urandom(32).hex()
    
    # Create .env content
    env_content = f"""# Strava API Configuration
STRAVA_CLIENT_ID=164037
STRAVA_CLIENT_SECRET={client_secret}

# Google Maps API Key (required for traffic analysis)
GOOGLE_MAPS_API_KEY={maps_key}

# Flask Secret Key (auto-generated)
SECRET_KEY={secret_key}
"""
    
    # Write .env file
    env_file = Path('.env')
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"\n✅ Created {env_file}")
    except Exception as e:
        print(f"\n❌ Error creating .env file: {e}")
        print("\nPlease create .env file manually with this content:")
        print("-" * 40)
        print(env_content)
        return
    
    print("\n🎉 Environment configuration complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip3 install -r requirements.txt")
    print("2. Test setup: python3 test_oauth_setup.py")
    print("3. Run dashboard: python3 web_dashboard.py")
    print("4. Visit: http://localhost:5000")

if __name__ == "__main__":
    main() 