# backend/app.py

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db, User, Subject, Chapter, Quiz, Question, Score

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    # Load config (DATABASE_URI, SECRET_KEY, etc.)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    # Health-check endpoint
    @app.route("/ping", methods=["GET"])
    def ping():
        return jsonify({"message": "pong"})

    return app

if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        # Create all tables for models that have been imported
        db.create_all()
        print("🔨  All tables created")

    # Start the Flask dev server
    app.run(host="0.0.0.0", port=5000, debug=True)
