import os
from flask import Flask, redirect, request, session
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv()

# Retrieve configuration values from the environment.
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET_KEY = os.getenv("TWITTER_API_SECRET_KEY")
TWITTER_CALLBACK_URL = os.getenv("TWITTER_CALLBACK_URL")  # e.g., "http://localhost:5000/callback"
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

# Twitter OAuth endpoints.
TWITTER_REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
TWITTER_AUTHORIZATION_URL = "https://api.twitter.com/oauth/authorize"
TWITTER_ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

@app.route('/')
def start_oauth():
    """
    Step 1: Start the OAuth process by obtaining a request token from Twitter.
    """
    oauth = OAuth1Session(
        client_key=TWITTER_API_KEY,
        client_secret=TWITTER_API_SECRET_KEY,
        callback_uri=TWITTER_CALLBACK_URL
    )
    # Obtain request token.
    fetch_response = oauth.fetch_request_token(TWITTER_REQUEST_TOKEN_URL)
    session['oauth_token'] = fetch_response.get('oauth_token')
    session['oauth_token_secret'] = fetch_response.get('oauth_token_secret')

    # Step 2: Redirect the user to Twitter for authorization.
    authorization_url = oauth.authorization_url(TWITTER_AUTHORIZATION_URL)
    return redirect(authorization_url)

@app.route('/callback')
def oauth_callback():
    """
    Step 3: Handle the callback from Twitter, exchanging the request token and verifier for an access token.
    """
    oauth_verifier = request.args.get('oauth_verifier')
    oauth_token = request.args.get('oauth_token')

    # Retrieve the original request token from the session.
    resource_owner_key = session.get('oauth_token')
    resource_owner_secret = session.get('oauth_token_secret')

    if oauth_token != resource_owner_key:
        return "Error: OAuth token mismatch.", 400

    # Create a new OAuth1Session with the verifier to obtain the access token.
    oauth = OAuth1Session(
        client_key=TWITTER_API_KEY,
        client_secret=TWITTER_API_SECRET_KEY,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=oauth_verifier
    )
    
    # Step 4: Fetch the access token.
    oauth_tokens = oauth.fetch_access_token(TWITTER_ACCESS_TOKEN_URL)
    access_token = oauth_tokens.get('oauth_token')
    access_token_secret = oauth_tokens.get('oauth_token_secret')

    # You can now use these tokens to access the Twitter API on behalf of the user.
    return (
        f"Access Token: {access_token}<br>"
        f"Access Token Secret: {access_token_secret}"
    )

if __name__ == '__main__':
    # Run the app in debug mode for development.
    app.run(debug=True)
