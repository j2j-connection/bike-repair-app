# Strava Traffic Monitor - OAuth Authentication

This version of the Strava Traffic Monitor now supports OAuth authentication, allowing anyone to log into their own Strava account and view their personal commute comparisons.

## 🚀 Quick Start

### 1. Set Up Your Strava App

Run the setup script to configure OAuth authentication:

```bash
python setup_strava_app.py
```

This will guide you through:
- Creating a Strava API application
- Setting up environment variables
- Configuring the necessary files

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Google Maps API

Add your Google Maps API key to the `.env` file:

```
GOOGLE_MAPS_API_KEY=your_actual_google_maps_api_key_here
```

### 4. Run the Dashboard

```bash
python web_dashboard.py
```

### 5. Access the Application

Visit `http://localhost:5000` and click "Login with Strava" to authenticate with your Strava account.

## 🔧 Configuration

### Environment Variables

The application uses the following environment variables (set in `.env` file):

- `STRAVA_CLIENT_ID`: Your Strava app client ID
- `STRAVA_CLIENT_SECRET`: Your Strava app client secret
- `GOOGLE_MAPS_API_KEY`: Google Maps API key for traffic analysis
- `SECRET_KEY`: Flask secret key (auto-generated)

### Strava App Settings

When creating your Strava app at https://www.strava.com/settings/api:

- **Application Name**: Traffic Monitor (or your preferred name)
- **Category**: Analytics
- **Website**: http://localhost:5000
- **Authorization Callback Domain**: localhost

## 🔐 OAuth Flow

1. **User clicks "Login with Strava"**
2. **Redirected to Strava authorization page**
3. **User authorizes the application**
4. **Strava redirects back with authorization code**
5. **Application exchanges code for access token**
6. **User is logged in and can view their data**

## 👥 Multi-User Support

- Each user authenticates with their own Strava account
- User sessions are managed securely
- Users can only see their own activity data
- Multiple users can use the application simultaneously

## 🔄 Session Management

- Access tokens are stored in server-side sessions
- Sessions are secure and encrypted
- Users can logout to clear their session
- Sessions persist until logout or browser close

## 🛡️ Security Features

- OAuth 2.0 authentication flow
- Secure session management
- Environment variable configuration
- No hardcoded credentials
- HTTPS-ready (for production)

## 🚀 Production Deployment

For production deployment:

1. **Set up HTTPS** (required for OAuth)
2. **Update redirect URI** in Strava app settings
3. **Set environment variables** on your server
4. **Use a proper WSGI server** (e.g., Gunicorn)
5. **Set up a reverse proxy** (e.g., Nginx)

### Example Production Configuration

```bash
# Set environment variables
export STRAVA_CLIENT_ID="your_client_id"
export STRAVA_CLIENT_SECRET="your_client_secret"
export GOOGLE_MAPS_API_KEY="your_google_maps_key"
export SECRET_KEY="your_secret_key"

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_dashboard:app
```

## 🔧 Troubleshooting

### Common Issues

1. **"Strava API not configured"**
   - Run `python setup_strava_app.py`
   - Ensure `.env` file exists with correct credentials

2. **"Authorization failed"**
   - Check redirect URI in Strava app settings
   - Ensure callback domain matches your setup

3. **"Monitor not available"**
   - Verify Google Maps API key is set
   - Check internet connection

4. **Session issues**
   - Clear browser cookies
   - Ensure SECRET_KEY is set

### Debug Mode

For debugging, you can enable Flask debug mode:

```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 📝 API Endpoints

- `GET /` - Main dashboard
- `GET /login` - Redirect to Strava OAuth
- `GET /oauth/callback` - OAuth callback handler
- `GET /logout` - Logout user
- `GET /api/user_info` - Get current user info
- `GET /api/comparisons` - Get user's traffic comparisons
- `GET /api/stats` - Get user's statistics
- `GET /api/status` - Get system status
- `POST /api/trigger_check` - Trigger manual activity check

## 🤝 Contributing

When contributing to this project:

1. **Never commit sensitive data** (API keys, tokens)
2. **Use environment variables** for configuration
3. **Test OAuth flow** thoroughly
4. **Follow security best practices**

## 📄 License

This project is open source. Please ensure you comply with Strava's API terms of service when using this application. 