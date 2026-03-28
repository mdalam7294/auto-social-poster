import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

def seo_optimize_caption(caption, keywords=None):
    """Add relevant hashtags to caption for better reach"""
    words = caption.lower().split()
    stopwords = {'a','an','and','are','as','at','be','but','by','for','in','is','it','of','on','or','the','to','with'}
    meaningful = [w for w in words if w not in stopwords and len(w) > 3]
    hashtags = list(set([f"#{h}" for h in meaningful[:5] if h.isalpha()]))
    # Add some generic tags if needed
    if not hashtags:
        hashtags = ["#viral", "#trending", "#youtube"]
    final_caption = caption + "\n\n" + " ".join(hashtags[:10])
    return final_caption

def upload_youtube_video(user, video_path, title, description, tags=None, privacy='public'):
    if not user.youtube_token:
        return "❌ YouTube not connected. Please connect your YouTube account from dashboard."

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

        # SEO optimized description
        optimized_desc = seo_optimize_caption(description, keywords=tags)

        body = {
            'snippet': {
                'title': title[:100],
                'description': optimized_desc[:5000],
                'tags': tags or [],
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': privacy
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
