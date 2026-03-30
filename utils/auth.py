import os
import requests
from google_auth_oauthlib.flow import Flow
from flask import url_for, session, redirect
from flask_login import current_user
from models import db, YouTubeChannel
import json

def get_youtube_flow():
    return Flow.from_client_secrets_file(
        os.getenv('YOUTUBE_CLIENT_SECRETS_FILE'),
        scopes=['https://www.googleapis.com/auth/youtube.upload',
                'https://www.googleapis.com/auth/youtube.readonly'],
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

    # Get channel information from YouTube API
    token = credentials.token
    refresh_token = credentials.refresh_token
    client_id = credentials.client_id
    client_secret = credentials.client_secret
    token_uri = credentials.token_uri

    # Call YouTube API to get the channel details
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get('https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true', headers=headers)
    if resp.status_code != 200:
        return False
    data = resp.json()
    if not data.get('items'):
        return False
    channel = data['items'][0]
    channel_id = channel['id']
    channel_title = channel['snippet']['title']

    # Check if channel already exists for this user
    existing = YouTubeChannel.query.filter_by(user_id=current_user.id, channel_id=channel_id).first()
    if existing:
        # Update token
        existing.access_token = {
            'token': token,
            'refresh_token': refresh_token,
            'token_uri': token_uri,
            'client_id': client_id,
            'client_secret': client_secret,
            'scopes': credentials.scopes
        }
    else:
        new_channel = YouTubeChannel(
            user_id=current_user.id,
            channel_id=channel_id,
            channel_title=channel_title,
            access_token={
                'token': token,
                'refresh_token': refresh_token,
                'token_uri': token_uri,
                'client_id': client_id,
                'client_secret': client_secret,
                'scopes': credentials.scopes
            }
        )
        db.session.add(new_channel)
    db.session.commit()
    return True
