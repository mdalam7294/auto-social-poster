import os
from google_auth_oauthlib.flow import Flow
from flask import url_for, session
from flask_login import current_user
from models import db

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
