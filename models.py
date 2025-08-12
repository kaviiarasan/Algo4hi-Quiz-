from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to submissions
    submissions = db.relationship('QuizSubmission', backref='user', lazy=True)

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    question1 = db.Column(db.Text, nullable=False)
    question1_options = db.Column(db.JSON, nullable=False)  # List of options (2-6)
    question1_correct = db.Column(db.Integer, nullable=False)  # Index of correct answer
    question2 = db.Column(db.Text, nullable=False)
    question2_options = db.Column(db.JSON, nullable=False)  # List of options (2-6)
    question2_correct = db.Column(db.Integer, nullable=False)  # Index of correct answer
    is_locked = db.Column(db.Boolean, default=False)
    results_published = db.Column(db.Boolean, default=False)
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    quiz_url = db.Column(db.String(100), unique=True, nullable=True)  # Unique URL for direct access
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to submissions
    submissions = db.relationship('QuizSubmission', backref='quiz', lazy=True)
    winner = db.relationship('User', foreign_keys=[winner_id])

class Winner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo_url = db.Column(db.String(200), nullable=True)
    achievement = db.Column(db.String(200), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=True)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    quiz = db.relationship('Quiz', backref='winner_showcases')

class QuizSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    answer1 = db.Column(db.Integer, nullable=False)  # Index of selected answer (0-3)
    answer2 = db.Column(db.Integer, nullable=False)  # Index of selected answer (0-3)
    time_taken = db.Column(db.Integer, nullable=False)  # Time in seconds
    score = db.Column(db.Integer, nullable=False)
    bonus_awarded = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent multiple submissions per user per quiz
    __table_args__ = (db.UniqueConstraint('user_id', 'quiz_id', name='unique_user_quiz_submission'),)
