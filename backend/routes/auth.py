#backend/routes/auth.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity,verify_jwt_in_request
from app import db
from models import User, ActivityLog
from datetime import datetime
from extensions import limiter, cache

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")  # max 5 registrations per IP/min
def register():
    data = request.get_json() or {}
    email     = data.get('email')
    password  = data.get('password')
    full_name = data.get('full_name')
    
    # Basic validation
    if not email or not password or not full_name:
        return jsonify(msg='Email, password, and full_name are required'), 400

    if User.query.filter_by(email=email).first():
        return jsonify(msg='Email already registered'), 400

    # Parse optional DOB
    dob = None
    dob_str = data.get('dob')
    if dob_str:
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify(msg='Invalid dob format; use YYYY-MM-DD'), 400
        
    # Create user
    user = User(
        email=email,
        full_name=full_name,
        qualification=data.get('qualification'),
        dob=dob,
        is_admin=False
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Log the activity
    log = ActivityLog(
        type="registration",
        user=user.full_name,
        message=f"New user '{user.full_name}' registered."
    )
    db.session.add(log)
    db.session.commit()

    # Generate JWT for new user
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"is_admin": False}
    )

    return jsonify(
        access_token=access_token,
        id=user.id,
        email=user.email,
        full_name=user.full_name
    ), 201

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")  
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')

    if not email or not password or not full_name:
        return jsonify(msg='Missing email, full name or password'), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad credentials"}), 401
    
    if user.full_name.lower() != full_name.strip().lower():
        return jsonify({"msg": "Full name does not match"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"is_admin": user.is_admin}
    )

    return jsonify(access_token=access_token), 200


@auth_bp.route("/me", methods=["GET", "OPTIONS"])
@jwt_required() 
@cache.cached(timeout=60, key_prefix=lambda: f"user_me:{get_jwt_identity()}")
def me():
    if request.method == "OPTIONS":
        return '', 200  # respond to preflight

    verify_jwt_in_request()  # manually verify since we didn’t use @jwt_required
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    return jsonify({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "qualification": user.qualification,
        "dob": user.dob.isoformat() if user.dob else None,
        "is_admin": user.is_admin
    }), 200
