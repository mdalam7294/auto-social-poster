import tweepy
from flask import url_for, session, redirect
from flask_login import current_user
from models import db
import os
import requests

# ---------- Twitter OAuth ----------
def twitter_oauth_url():
    auth = tweepy.OAuth1UserHandler(
        os.getenv('TWITTER_API_KEY'),
        os.getenv('TWITTER_API_SECRET'),
        callback=url_for('twitter_callback', _external=True)
    )
    try:
        redirect_url = auth.get_authorization_url()
        session['twitter_request_token'] = auth.request_token
        return redirect_url
    except Exception as e:
        print(f"Twitter OAuth Error: {e}")
        return None

def twitter_callback_handler(oauth_verifier):
    request_token = session.get('twitter_request_token')
    if not request_token:
        return False
    
    auth = tweepy.OAuth1UserHandler(
        os.getenv('TWITTER_API_KEY'),
        os.getenv('TWITTER_API_SECRET')
    )
    auth.request_token = request_token
    
    try:
        access_token, access_secret = auth.get_access_token(oauth_verifier)
        current_user.twitter_token = {
            'access_token': access_token,
            'access_secret': access_secret
        }
        db.session.commit()
        return True
    except Exception as e:
        print(f"Twitter callback error: {e}")
        return False

# ---------- Facebook OAuth (simplified - page token already in .env) ----------
# Facebook page token directly use kar rahe hain, OAuth flow nahi

# ---------- YouTube OAuth ----------
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import pickle

def get_youtube_flow():
    return Flow.from_client_secrets_file(
        os.getenv('YOUTUBE_CLIENT_SECRETS_FILE'),
        scopes=['https://www.googleapis.com/auth/youtube.upload',
                'https://www.googleapis.com/auth/youtube'],
        redirect_uri=url_for('youtube_callback', _external=True)
    )

def youtube_auth_url():
    flow = get_youtube_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['youtube_state'] = state
    return authorization_url

def youtube_callback_handler(code, state):
    if state != session.get('youtube_state'):
        return False
    
    flow = get_youtube_flow()
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Save credentials
    current_user.youtube_token = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    db.session.commit()
    return True
