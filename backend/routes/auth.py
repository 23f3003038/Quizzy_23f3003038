#backend/routes/auth.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from models import User
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify(msg='No input data provided'), 400

    email     = data.get('email')
    password  = data.get('password')
    full_name = data.get('full_name')
    if not email or not password or not full_name:
        return jsonify(msg='Missing email, password, or full_name'), 400

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

    return jsonify(
        id=user.id,
        email=user.email,
        full_name=user.full_name
    ), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify(msg='Missing email or password'), 400
    
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not user.check_password(data.get("password")):
        return jsonify({"msg": "Bad credentials"}), 401

    # additional claims: is_admin
    additional_claims = {"is_admin": user.is_admin}
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

    return jsonify(access_token=access_token), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    return jsonify({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "qualification": user.qualification,
        "dob": user.dob.isoformat() if user.dob else None,
        "is_admin": user.is_admin
    }), 200
