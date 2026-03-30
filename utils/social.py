from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from models import YouTubeChannel

def upload_youtube_video(channel_id, video_path, title, description, tags=None, privacy='public'):
    # Fetch the channel token from database
    channel = YouTubeChannel.query.get(channel_id)
    if not channel:
        return "❌ Channel not found"
    token_data = channel.access_token

    try:
        creds = Credentials(
            token=token_data['token'],
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=token_data['scopes']
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
        return f"✅ Uploaded to {channel.channel_title}: https://youtu.be/{video_id}"
    except Exception as e:
        return f"❌ YouTube error: {str(e)}"
