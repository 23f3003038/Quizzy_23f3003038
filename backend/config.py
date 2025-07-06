#backend/config.py 

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "quizzy.db") 

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///" + db_path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = ["http://localhost:5173"]
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-prod")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "a-very-secret-key") 
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_HEADER_NAME            = "Authorization"
    JWT_HEADER_TYPE            = "Bearer"