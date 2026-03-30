from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class YouTubeChannel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.String(100), unique=True, nullable=False)
    channel_title = db.Column(db.String(200))
    access_token = db.Column(db.JSON, nullable=False)   # store token as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='youtube_channels')
