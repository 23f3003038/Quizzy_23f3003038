# backend/models/__init__.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .models import User, Subject, Chapter, Quiz, Question, Score

__all__ = [
    "db",
    "User",
    "Subject",
    "Chapter",
    "Quiz",
    "Question",
    "Score",
]