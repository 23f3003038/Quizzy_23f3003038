# backend/models/__init__.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

from .models import User, Subject, Chapter, Quiz, Question, Score

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)   # e.g., 'registration', 'quiz_created'
    user = db.Column(db.String(100))                  # name or email of user involved
    quiz = db.Column(db.Integer)                      # quiz ID (if applicable)
    quiz_name = db.Column(db.String(255))             # optional quiz/subject name
    admin = db.Column(db.String(100))                 # admin's name if applicable
    message = db.Column(db.Text)                      # fallback message
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ActivityLog {self.type} at {self.timestamp}>"

__all__ = [
    "db",
    "User",
    "Subject",
    "Chapter",
    "Quiz",
    "Question",
    "Score",
    "ActivityLog"
]