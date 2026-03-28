from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User
from utils.social import upload_youtube_video
from utils.auth import youtube_auth_url, youtube_callback_handler
import os
from dotenv import load_dotenv
import secrets

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

@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    if request.method == 'POST':
        caption = request.form['caption']
        title = request.form.get('title', caption[:80])
        tags = [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()]
        privacy = request.form.get('privacy', 'public')

        media_file = request.files.get('media')
        if not media_file or not media_file.filename:
            flash('Please select a video file to upload.')
            return redirect(url_for('post'))

        # Check if it's a video
        if not media_file.mimetype.startswith('video/'):
            flash('Only video files are supported.')
            return redirect(url_for('post'))

        # Save temporarily
        filename = f"static/temp/{secrets.token_hex(8)}_{media_file.filename}"
        media_file.save(filename)

        # Upload to YouTube
        result = upload_youtube_video(current_user, filename, title, caption, tags, privacy)

        # Clean up temp file
        if os.path.exists(filename):
            os.remove(filename)

        return render_template('result.html', results={'YouTube': result})

    return render_template('post.html')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
