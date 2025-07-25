# backend/app.py

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import User
from extensions import db, jwt, mail
from celery import Celery
from celery_app import init_celery
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    init_celery(app)

    CORS(
    app,
    resources={r"/api/*": {"origins": ["http://localhost:5173"]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # Auth routes (login / register)
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Admin routes
    from routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # User routes
    from routes.user import user_bp
    app.register_blueprint(user_bp, url_prefix="/api/user")

    @app.after_request
    def apply_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response


    return app

if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        db.create_all()

        # Seed the built-in admin if it doesn’t exist
        if not User.query.filter_by(email="admin@quizzy.local").first():
            admin = User(
                email="admin@quizzy.local",
                full_name="Quizzy Admin",
                qualification="Quiz Master",
                dob=None,
                is_admin=True
            )
            admin.set_password("ChangeMe123")
            db.session.add(admin)
            db.session.commit()
            print("🛡️  Seeded admin user (admin@quizzy.local)")

        print("🔨  All tables created")

    # Launch
    app.run(host="0.0.0.0", port=5000, debug=True)
