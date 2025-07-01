#backend/config.py 

import os

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "quizzy.db") 

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///" + db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = "*"
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod") 