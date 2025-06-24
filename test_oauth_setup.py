#!/usr/bin/env python3
"""
Test OAuth Setup

This script tests the OAuth configuration to ensure everything is set up correctly.
"""

import os
import sys
from pathlib import Path

def test_env_file():
    """Test if .env file exists and has required variables."""
    print("🔍 Testing .env file...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   Run: python setup_strava_app.py")
        return False
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment")
    
    required_vars = ['STRAVA_CLIENT_ID', 'STRAVA_CLIENT_SECRET', 'GOOGLE_MAPS_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.environ.get(var)
        if not value or value == f'your_{var.lower()}_here':
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {value[:10]}...")
    
    if missing_vars:
        print(f"❌ Missing or invalid variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ .env file configuration looks good!")
    return True

def test_config_file():
    """Test if config.py is properly configured."""
    print("\n🔍 Testing config.py...")
    
    config_file = Path('config.py')
    if not config_file.exists():
        print("❌ config.py not found!")
        return False
    
    try:
        from config import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, GOOGLE_MAPS_API_KEY
        print("✅ config.py imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Error importing config.py: {e}")
        return False

def test_dependencies():
    """Test if required dependencies are installed."""
    print("\n🔍 Testing dependencies...")
    
    required_packages = ['flask', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def test_web_dashboard():
    """Test if web dashboard can be imported."""
    print("\n🔍 Testing web dashboard...")
    
    try:
        import web_dashboard
        print("✅ web_dashboard.py imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Error importing web_dashboard.py: {e}")
        return False

def test_strava_api():
    """Test basic Strava API connectivity."""
    print("\n🔍 Testing Strava API connectivity...")
    
    try:
        client_id = os.environ.get('STRAVA_CLIENT_ID')
        if not client_id or client_id == 'your_strava_client_id_here':
            print("❌ STRAVA_CLIENT_ID not configured")
            return False
        
        import requests
        # Test basic API endpoint
        response = requests.get("https://www.strava.com/api/v3/athlete", 
                              headers={"Authorization": "Bearer test"})
        
        if response.status_code in [401, 403]:  # Expected for invalid token
            print("✅ Strava API is accessible")
            return True
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            return True
            
    except Exception as e:
        print(f"❌ Error testing Strava API: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 OAuth Setup Test")
    print("=" * 40)
    
    tests = [
        test_env_file,
        test_config_file,
        test_dependencies,
        test_web_dashboard,
        test_strava_api
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OAuth setup is ready.")
        print("\nNext steps:")
        print("1. Run: python web_dashboard.py")
        print("2. Visit: http://localhost:5000")
        print("3. Click 'Login with Strava'")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Run: python setup_strava_app.py")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Check your .env file configuration")

if __name__ == "__main__":
    main() 