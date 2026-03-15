from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User
from utils.social import post_to_all
from utils.rewriter import rewrite_article, seo_optimize
from utils.extractor import extract_from_url
from utils.auth import twitter_oauth_url, twitter_callback_handler, youtube_auth_url, youtube_callback_handler
import os
from dotenv import load_dotenv
import secrets

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///tokens/users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create upload folder
os.makedirs('static/temp', exist_ok=True)
os.makedirs('tokens', exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        # Hash password and create user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# ---------- Twitter OAuth Routes ----------
@app.route('/connect/twitter')
@login_required
def connect_twitter():
    auth_url = twitter_oauth_url()
    if auth_url:
        return redirect(auth_url)
    flash('Failed to connect to Twitter')
    return redirect(url_for('dashboard'))

@app.route('/twitter/callback')
@login_required
def twitter_callback():
    oauth_verifier = request.args.get('oauth_verifier')
    if oauth_verifier and twitter_callback_handler(oauth_verifier):
        flash('Twitter connected successfully!')
    else:
        flash('Twitter connection failed')
    return redirect(url_for('dashboard'))

# ---------- YouTube OAuth Routes ----------
@app.route('/connect/youtube')
@login_required
def connect_youtube():
    auth_url = youtube_auth_url()
    return redirect(auth_url)

@app.route('/youtube/callback')
@login_required
def youtube_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if code and state and youtube_callback_handler(code, state):
        flash('YouTube connected successfully!')
    else:
        flash('YouTube connection failed')
    return redirect(url_for('dashboard'))

# ---------- Post Creation Route ----------
@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    if request.method == 'POST':
        # Get form data
        platforms = request.form.getlist('platforms')
        caption = request.form['caption']
        link = request.form.get('link', '')
        video_id = request.form.get('video_id', '')
        subreddit = request.form.get('subreddit', 'test')
        title = request.form.get('title', caption[:100])
        
        # Handle image upload
        image = request.files.get('image')
        image_path = None
        if image and image.filename:
            image_path = f"static/temp/{secrets.token_hex(8)}_{image.filename}"
            image.save(image_path)
        
        # Prepare data for posting
        post_data = {
            'platforms': platforms,
            'caption': caption,
            'image_path': image_path,
            'link': link,
            'video_id': video_id,
            'subreddit': subreddit,
            'title': title
        }
        
        # Post to all selected platforms
        results = post_to_all(current_user, post_data)
        
        return render_template('result.html', results=results)
    
    return render_template('post.html')

# ---------- Blog Rewrite and Post Route ----------
@app.route('/blog', methods=['GET', 'POST'])
@login_required
def blog():
    if request.method == 'POST':
        url = request.form['article_url']
        
        # Extract article
        article_data = extract_from_url(url)
        
        if article_data['title'] == 'Error':
            flash(article_data['text'])
            return redirect(url_for('blog'))
        
        # Rewrite article
        original_text = article_data['text']
        rewritten_text = rewrite_article(original_text)
        
        # SEO Optimize
        seo_title, seo_content, meta_desc = seo_optimize(article_data['title'], rewritten_text)
        
        # Post to Blogger
        result = post_blogger(current_user, seo_title, seo_content, 
                             labels=['rewritten', 'ai', 'seo-optimized'])
        
        flash(result)
        return redirect(url_for('dashboard'))
    
    return render_template('blog_form.html')

# ---------- Initialize Database ----------
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
