import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def upload_youtube_video(user, video_path, title, description, tags=None, privacy='public'):
    if not user.youtube_token:
        return "❌ YouTube not connected."

    try:
        creds = Credentials(
            token=user.youtube_token['token'],
            refresh_token=user.youtube_token.get('refresh_token'),
            token_uri=user.youtube_token['token_uri'],
            client_id=user.youtube_token['client_id'],
            client_secret=user.youtube_token['client_secret'],
            scopes=user.youtube_token['scopes']
        )
        youtube = build('youtube', 'v3', credentials=creds)

        body = {
            'snippet': {
                'title': title[:100],
                'description': description[:5000],
                'tags': tags or [],
                'categoryId': '22',
                'defaultLanguage': 'en'
            },
            'status': {
                'privacyStatus': privacy,
                'selfDeclaredMadeForKids': False
            }
        }
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        response = request.execute()
        video_id = response['id']
        return f"✅ YouTube video uploaded: https://youtu.be/{video_id}"
    except Exception as e:
        return f"❌ YouTube error: {str(e)}"
