from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from models import db, Subject

admin_bp = Blueprint("admin", __name__)

def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Validate JWT and ensure is_admin==True
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims.get("is_admin"):
            return jsonify(msg="Admins only"), 403
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route("/subjects", methods=["POST"])
@require_admin  
def create_subject():
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify(msg="Name is required"), 400

    subject = Subject(name=name, description=data.get("description"))
    db.session.add(subject)
    db.session.commit()

    return jsonify(id=subject.id, name=subject.name, description=subject.description), 201

@admin_bp.route("/subjects", methods=["GET"])
@require_admin 
def list_subjects():
    subjects = Subject.query.all()
    result = [
        {"id": s.id, "name": s.name, "description": s.description}
        for s in subjects
    ]
    return jsonify(result), 200
