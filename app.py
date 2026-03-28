from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User
from utils.auth import youtube_auth_url, youtube_callback_handler
from utils.downloader import download_video
from utils.transformer import recreate_video
from utils.seo import generate_high_rpm_seo
from utils.scheduler import schedule_upload
from utils.social import upload_youtube_video
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///tokens/users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

os.makedirs('static/temp', exist_ok=True)
os.makedirs('tokens', exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------- Routes -------------------
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
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
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

@app.route('/process', methods=['GET', 'POST'])
@login_required
def process():
    if request.method == 'POST':
        video_url = request.form['video_url']
        if not video_url:
            flash('Please enter a video URL')
            return redirect(url_for('process'))

        try:
            # 1. Download video
            temp_video = f"static/temp/{secrets.token_hex(8)}_original.mp4"
            download_video(video_url, temp_video)

            # 2. Recreate video (audio replacement, translation)
            final_video = f"static/temp/{secrets.token_hex(8)}_final.mp4"
            final_video = recreate_video(video_url, final_video)  # uses temp_video internally

            # 3. Generate SEO metadata
            title = "Amazing Content"  # could extract from original or AI
            description = "Check out this amazing video recreated with AI for English audience."
            tags = ["viral", "trending", "ai"]
            title, description, tags = generate_high_rpm_seo(title, description, tags)

            metadata = {
                'title': title,
                'description': description,
                'tags': tags,
                'privacy': 'public'
            }

            # 4. Schedule upload (or immediate)
            result = schedule_upload(upload_youtube_video, final_video, metadata, current_user)

            # Clean up temp files
            os.remove(temp_video)
            # Keep final_video? we'll keep for a while, maybe delete after upload. For simplicity, keep.
            return render_template('result.html', result=result)

        except Exception as e:
            flash(f"Error: {str(e)}")
            return redirect(url_for('process'))

    return render_template('process.html')

# Ensure database created
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
