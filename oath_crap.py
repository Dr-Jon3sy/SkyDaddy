import os
from flask import Flask, redirect, request, session, jsonify
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv

# Load environment variables from the .env file.
load_dotenv()

# Retrieve configuration values from the environment.
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET_KEY = os.getenv("TWITTER_API_SECRET_KEY")
TWITTER_CALLBACK_URL = os.getenv("TWITTER_CALLBACK_URL")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

# Twitter OAuth endpoints.
TWITTER_REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
TWITTER_AUTHORIZATION_URL = "https://api.twitter.com/oauth/authorize"
TWITTER_ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

# Twitter API endpoint to get the user's timeline.
TWITTER_USER_TIMELINE_URL = "https://api.twitter.com/1.1/statuses/user_timeline.json"

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
    # Obtain a request token.
    fetch_response = oauth.fetch_request_token(TWITTER_REQUEST_TOKEN_URL)
    session['oauth_token'] = fetch_response.get('oauth_token')
    session['oauth_token_secret'] = fetch_response.get('oauth_token_secret')

    # Redirect the user to Twitter for authorization.
    authorization_url = oauth.authorization_url(TWITTER_AUTHORIZATION_URL)
    return redirect(authorization_url)

@app.route('/callback')
def oauth_callback():
    """
    Step 3: Handle the callback from Twitter by exchanging the request token and verifier for an access token.
    """
    oauth_verifier = request.args.get('oauth_verifier')
    oauth_token = request.args.get('oauth_token')

    # Retrieve the original request token from the session.
    resource_owner_key = session.get('oauth_token')
    resource_owner_secret = session.get('oauth_token_secret')

    if oauth_token != resource_owner_key:
        return "Error: OAuth token mismatch.", 400

    # Create an OAuth1Session with the verifier to obtain the access token.
    oauth = OAuth1Session(
        client_key=TWITTER_API_KEY,
        client_secret=TWITTER_API_SECRET_KEY,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=oauth_verifier
    )
    
    # Fetch the access token.
    oauth_tokens = oauth.fetch_access_token(TWITTER_ACCESS_TOKEN_URL)
    access_token = oauth_tokens.get('oauth_token')
    access_token_secret = oauth_tokens.get('oauth_token_secret')

    # Store the access tokens in the session for subsequent API calls.
    session['access_token'] = access_token
    session['access_token_secret'] = access_token_secret

    return (
        f"Access Token: {access_token}<br>"
        f"Access Token Secret: {access_token_secret}<br>"
        "Now, access /latest_tweet to retrieve your most recent tweet."
    )

@app.route('/latest_tweet')
def latest_tweet():
    """
    Retrieve the most recent tweet from the authenticated user's timeline.
    """
    access_token = session.get('access_token')
    access_token_secret = session.get('access_token_secret')

    if not access_token or not access_token_secret:
        return "User not authenticated. Please authenticate via Twitter OAuth.", 400

    # Create an OAuth1Session using the stored access tokens.
    oauth = OAuth1Session(
        client_key=TWITTER_API_KEY,
        client_secret=TWITTER_API_SECRET_KEY,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret
    )

    # Set parameters to fetch only the most recent tweet. 'tweet_mode=extended' ensures full text is returned.
    params = {'count': 1, 'tweet_mode': 'extended'}
    response = oauth.get(TWITTER_USER_TIMELINE_URL, params=params)

    if response.status_code != 200:
        return f"Failed to fetch tweet: {response.text}", response.status_code

    tweets = response.json()
    if tweets:
        # Return the most recent tweet as JSON.
        return jsonify(tweets[0])
    else:
        return "No tweets found.", 404

if __name__ == '__main__':
    app.run(debug=True)
