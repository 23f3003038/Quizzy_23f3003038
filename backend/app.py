# backend/app.py

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db, User, Subject, Chapter, Quiz, Question, Score
from flask_jwt_extended import JWTManager

jwt = JWTManager()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    # Load config (DATABASE_URI, SECRET_KEY, etc.)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    # Health-check endpoint
    @app.route("/ping", methods=["GET"])
    def ping():
        return jsonify({"message": "pong"})
    
    # Register blueprints
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    from routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    from routes.user import user_bp
    app.register_blueprint(user_bp, url_prefix="/api/user")

    return app

if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        # Create all tables for models that have been imported
        db.create_all()
        # Seed default admin user if desired:
        if not User.query.filter_by(email="admin@quizzy.local").first():
            admin = User(
                email="admin@quizzy.local",
                full_name="Quizzy Admin",
                qualification="",
                dob=None,
                is_admin=True
            )
            admin.set_password("ChangeMe123!")
            db.session.add(admin)
            db.session.commit()
            print("🛡️  Seeded admin user (admin@quizzy.local)")

        print("🔨  All tables created")

    # Start the Flask dev server
    app.run(host="0.0.0.0", port=5000, debug=True)
