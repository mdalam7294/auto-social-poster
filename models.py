from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Store hashed password
    
    # OAuth tokens stored as JSON
    twitter_token = db.Column(db.JSON)
    facebook_token = db.Column(db.JSON)
    instagram_token = db.Column(db.JSON)
    pinterest_token = db.Column(db.JSON)
    reddit_token = db.Column(db.JSON)
    youtube_token = db.Column(db.JSON)
    blogger_token = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
