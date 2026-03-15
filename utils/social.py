import tweepy
import facebook
import requests
import praw
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import os
import base64
from datetime import datetime

# ---------- Twitter Post ----------
def post_twitter(user, text, image_path=None):
    """Twitter par post karo"""
    if not user.twitter_token:
        return "❌ Twitter not connected"
    
    auth = tweepy.OAuth1UserHandler(
        os.getenv('TWITTER_API_KEY'),
        os.getenv('TWITTER_API_SECRET'),
        user.twitter_token['access_token'],
        user.twitter_token['access_secret']
    )
    api = tweepy.API(auth)
    
    try:
        if image_path and os.path.exists(image_path):
            media = api.media_upload(image_path)
            api.update_status(status=text, media_ids=[media.media_id])
        else:
            api.update_status(status=text)
        return "✅ Twitter post successful"
    except Exception as e:
        return f"❌ Twitter error: {str(e)}"

# ---------- Facebook Post ----------
def post_facebook(user, text, image_path=None, link=None):
    """Facebook page par post karo"""
    token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
    page_id = os.getenv('FACEBOOK_PAGE_ID')
    
    if not token or not page_id:
        return "❌ Facebook not configured"
    
    graph = facebook.GraphAPI(access_token=token)
    
    try:
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as img:
                graph.put_photo(image=img, message=text, album_path=f"{page_id}/photos")
        elif link:
            graph.put_object(parent_object=page_id, connection_name='feed', 
                            message=text, link=link)
        else:
            graph.put_object(parent_object=page_id, connection_name='feed', 
                            message=text)
        return "✅ Facebook post successful"
    except Exception as e:
        return f"❌ Facebook error: {str(e)}"

# ---------- Instagram Post ----------
def post_instagram(user, image_path, caption):
    """Instagram par post karo (Business account required)"""
    ig_id = os.getenv('INSTAGRAM_BUSINESS_ID')
    token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
    
    if not ig_id or not token:
        return "❌ Instagram not configured"
    
    try:
        # Step 1: Upload media
        url = f"https://graph.facebook.com/v18.0/{ig_id}/media"
        with open(image_path, 'rb') as img:
            files = {'image': img}
            data = {'caption': caption, 'access_token': token}
            response = requests.post(url, data=data, files=files)
        
        if response.status_code != 200:
            return f"❌ Instagram upload error: {response.text}"
        
        creation_id = response.json().get('id')
        
        # Step 2: Publish
        publish_url = f"https://graph.facebook.com/v18.0/{ig_id}/media_publish"
        publish_data = {'creation_id': creation_id, 'access_token': token}
        publish_res = requests.post(publish_url, data=publish_data)
        
        if publish_res.status_code == 200:
            return "✅ Instagram post successful"
        else:
            return f"❌ Instagram publish error: {publish_res.text}"
    except Exception as e:
        return f"❌ Instagram error: {str(e)}"

# ---------- Pinterest Post ----------
def post_pinterest(user, image_path, title, description, link=None):
    """Pinterest par pin karo"""
    token = os.getenv('PINTEREST_ACCESS_TOKEN')
    if not token:
        return "❌ Pinterest not configured"
    
    try:
        # Pinterest API v5
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        
        # Upload image first
        with open(image_path, 'rb') as img:
            import requests
            upload_url = "https://api.pinterest.com/v5/media"
            files = {'media': img}
            upload_res = requests.post(upload_url, headers=headers, files=files)
            
            if upload_res.status_code != 201:
                return f"❌ Pinterest upload error: {upload_res.text}"
            
            media_id = upload_res.json().get('media_id')
        
        # Create pin
        pin_data = {
            'title': title[:100],
            'description': description[:500],
            'board_id': 'your_board_id',  # Aapko board ID dena hoga
            'media_source': {
                'source_type': 'image_id',
                'image_id': media_id
            }
        }
        
        if link:
            pin_data['link'] = link
        
        pin_res = requests.post('https://api.pinterest.com/v5/pins', 
                                headers=headers, json=pin_data)
        
        if pin_res.status_code == 201:
            return "✅ Pinterest pin created"
        else:
            return f"❌ Pinterest error: {pin_res.text}"
    except Exception as e:
        return f"❌ Pinterest exception: {str(e)}"

# ---------- Reddit Post ----------
def post_reddit(user, title, text=None, image_path=None, subreddit='test'):
    """Reddit par post karo"""
    try:
        reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            username=os.getenv('REDDIT_USERNAME'),
            password=os.getenv('REDDIT_PASSWORD'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
        sub = reddit.subreddit(subreddit)
        
        if image_path and os.path.exists(image_path):
            # Image post
            sub.submit_image(title, image_path)
        else:
            # Text post
            sub.submit(title, selftext=text or title)
        
        return f"✅ Reddit post successful in r/{subreddit}"
    except Exception as e:
        return f"❌ Reddit error: {str(e)}"

# ---------- YouTube Thumbnail Update ----------
def update_youtube_thumbnail(user, video_id, image_path):
    """YouTube video ka thumbnail change karo"""
    if not user.youtube_token:
        return "❌ YouTube not connected"
    
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
        
        request = youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(image_path)
        )
        response = request.execute()
        
        return f"✅ YouTube thumbnail updated for video {video_id}"
    except Exception as e:
        return f"❌ YouTube error: {str(e)}"

# ---------- Blogger Post ----------
def post_blogger(user, title, content, labels=None):
    """Blogger par article post karo"""
    api_key = os.getenv('BLOGGER_API_KEY')
    blog_id = os.getenv('BLOGGER_BLOG_ID')
    
    if not api_key or not blog_id:
        return "❌ Blogger not configured"
    
    try:
        service = build('blogger', 'v3', developerKey=api_key)
        
        body = {
            'kind': 'blogger#post',
            'title': title,
            'content': content,
            'labels': labels or ['auto-posted', 'ai-rewritten']
        }
        
        request = service.posts().insert(blogId=blog_id, body=body)
        response = request.execute()
        
        return f"✅ Blogger post published: {response.get('url')}"
    except Exception as e:
        return f"❌ Blogger error: {str(e)}"

# ---------- Multiple Platforms at Once ----------
def post_to_all(user, data):
    """
    Sabhi platforms par ek saath post karo
    data = {
        'caption': '...',
        'image_path': '...',
        'link': '...',
        'video_id': '...',
        'subreddit': '...',
        'title': '...',
        'blog_content': '...'
    }
    """
    results = {}
    
    # Twitter
    if 'twitter' in data.get('platforms', []):
        results['twitter'] = post_twitter(user, data['caption'], data.get('image_path'))
    
    # Facebook
    if 'facebook' in data.get('platforms', []):
        results['facebook'] = post_facebook(user, data['caption'], 
                                           data.get('image_path'), data.get('link'))
    
    # Instagram
    if 'instagram' in data.get('platforms', []) and data.get('image_path'):
        results['instagram'] = post_instagram(user, data['image_path'], data['caption'])
    
    # Pinterest
    if 'pinterest' in data.get('platforms', []) and data.get('image_path'):
        results['pinterest'] = post_pinterest(user, data['image_path'], 
                                              data.get('title', data['caption']), 
                                              data['caption'], data.get('link'))
    
    # Reddit
    if 'reddit' in data.get('platforms', []):
        results['reddit'] = post_reddit(user, data.get('title', data['caption']),
                                        data['caption'], data.get('image_path'),
                                        data.get('subreddit', 'test'))
    
    # YouTube
    if 'youtube' in data.get('platforms', []) and data.get('video_id') and data.get('image_path'):
        results['youtube'] = update_youtube_thumbnail(user, data['video_id'], data['image_path'])
    
    # Blogger
    if 'blogger' in data.get('platforms', []) and data.get('blog_content'):
        results['blogger'] = post_blogger(user, data.get('title', 'Blog Post'), 
                                         data['blog_content'], data.get('labels'))
    
    return results
