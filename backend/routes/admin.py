# backend/routes/admin.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from functools import wraps
from models import db, Subject, Chapter, Quiz, Question, User, Score, ActivityLog
from datetime import datetime, timedelta
from extensions import cache, limiter

admin_bp = Blueprint("admin", __name__)

def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims.get("is_admin"):
            return jsonify(msg="Admins only"), 403
        return fn(*args, **kwargs)
    return wrapper

# ------- Subjects CRUD -------

@admin_bp.route("/subjects", methods=["GET"])
@require_admin
@cache.cached(timeout=300, key_prefix="admin_subject_list")
@limiter.limit("30/minute")
def list_subjects():
    subjects = Subject.query.all()
    return jsonify([
        {"id": s.id, "name": s.name, "description": s.description}
        for s in subjects
    ]), 200

@admin_bp.route("/subjects", methods=["POST"])
@require_admin
def create_subject():
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify(msg="Name is required"), 400
    
    existing = Subject.query.filter_by(name=name).first()
    if existing:
        return jsonify({"error": "Subject already exists"}), 409

    subject = Subject(name=name, description=data.get("description"))
    db.session.add(subject)
    # Log activity
    admin_name = get_jwt().get("full_name", "Admin")
    log = ActivityLog(
        type="subject_created",
        user=admin_name,
        message=f"Subject '{name}' was created."
    )
    db.session.add(log)

    db.session.commit()
    cache.delete("admin_subject_list")
    return jsonify(id=subject.id, name=subject.name, description=subject.description), 201

@admin_bp.route("/subjects/<int:id>", methods=["PUT", "DELETE"])
@require_admin
def modify_subject(id):
    subj = Subject.query.get_or_404(id)
    if request.method == "PUT":
        data = request.get_json() or {}
        if not data.get("name"):
            return jsonify(msg="Name is required"), 400
        subj.name = data["name"]
        subj.description = data.get("description")
        db.session.commit()
        cache.delete("admin_subject_list")
        return jsonify(id=subj.id, name=subj.name, description=subj.description), 200
    else:
        db.session.delete(subj)
        db.session.commit()
        cache.delete("admin_subject_list")
        return "", 204


# ------- Chapters CRUD -------

@admin_bp.route("/subjects/<int:subj_id>/chapters", methods=["GET", "POST"])
@require_admin
def chapters(subj_id):
    Subject.query.get_or_404(subj_id)
    if request.method == "GET":
        chapters = Chapter.query.filter_by(subject_id=subj_id).all()
        return jsonify([
            {"id": c.id, "name": c.name, "description": c.description}
            for c in chapters
        ]), 200

    # POST
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify(msg="Name is required"), 400
    existing = Chapter.query.filter_by(subject_id=subj_id, name=name).first()

    if existing:
        return jsonify(msg="Chapter with this name already exists in this subject."), 409
    
    chap = Chapter(subject_id=subj_id, name=name, description=data.get("description"))
    db.session.add(chap)
    db.session.commit()
    return jsonify(id=chap.id, name=chap.name, description=chap.description), 201

@admin_bp.route("/chapters/<int:id>", methods=["PUT", "DELETE"])
@require_admin
def modify_chapter(id):
    chap = Chapter.query.get_or_404(id)
    if request.method == "PUT":
        data = request.get_json() or {}
        if not data.get("name"):
            return jsonify(msg="Name is required"), 400
        chap.name = data["name"]
        chap.description = data.get("description")
        db.session.commit()
        return jsonify(id=chap.id, name=chap.name, description=chap.description), 200
    else:
        db.session.delete(chap)
        db.session.commit()
        return "", 204

# ------- Quizzes CRUD -------

@admin_bp.route("/quizzes", methods=["GET"])
@require_admin
@cache.cached(timeout=300, key_prefix="admin_quizzes_all")
@limiter.limit("20/minute")
def list_quizzes_global():
    """GET /api/admin/quizzes → returns every quiz"""
    quizzes = Quiz.query.all()
    return jsonify([
        {
            "id":           q.id,
            "chapter_id":   q.chapter_id,
            "name":         q.name,
            "description":  q.description,
            "deadline":     q.deadline.isoformat() if q.deadline else None,
            "duration":     str(q.duration),
            "remarks":      q.remarks
        }
        for q in quizzes
    ]), 200

@admin_bp.route("/quizzes/<int:id>", methods=["GET"])
@require_admin
@cache.cached(timeout=300, key_prefix=lambda: f"admin_quiz_{request.view_args['id']}")
def get_quiz_by_id(id):
    quiz = Quiz.query.get_or_404(id)
    chapter = Chapter.query.get(quiz.chapter_id)
    subject = Subject.query.get(chapter.subject_id) if chapter else None

    return jsonify({
        "id": quiz.id,
        "name": quiz.name,
        "description": quiz.description,
        "duration": str(quiz.duration),
        "deadline": quiz.deadline.isoformat() if quiz.deadline else None,
        "remarks": quiz.remarks,
        "chapter_id": chapter.id if chapter else None,
        "chapter_name": chapter.name if chapter else None,
        "subject_id": subject.id if subject else None,
        "subject_name": subject.name if subject else None
    }), 200

@admin_bp.route("/chapters/<int:chapter_id>/quizzes", methods=["POST"])
@require_admin
def create_quiz(chapter_id):
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        name = data.get("name")
        duration_str = data.get("duration")
        deadline_str = data.get("deadline")

        if not name or not duration_str or not deadline_str:
            return jsonify({"error": "Name, duration, and deadline are required."}), 400
        
        existing_quiz = Quiz.query.filter_by(chapter_id=chapter_id, name=name).first()
        if existing_quiz:
            return jsonify({"error": "Quiz with this name already exists in this chapter."}), 409

        # Parse duration (HH:MM)
        parts = list(map(int, duration_str.split(":")))
        if len(parts) == 2:
            h, m = parts
            s = 0
        elif len(parts) == 3:
            h, m, s = parts
        else:
            return jsonify({"error": "Invalid duration format. Use HH:MM or HH:MM:SS"}), 400

        duration = timedelta(hours=h, minutes=m, seconds=s)

        # Parse deadline (YYYY-MM-DD)
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d")

        quiz = Quiz(
            chapter_id=chapter_id,
            name=name,
            description=data.get("description"),
            duration=duration,
            deadline=deadline,
            remarks=data.get("remarks")
        )
        
        db.session.add(quiz)
        db.session.commit()
        cache.delete("admin_quizzes_all")
        cache.delete(f"admin_quizzes_chapter_{chapter_id}")
        return jsonify(quiz.to_dict()), 201

    except Exception as e:
        return jsonify({"error": f"Failed to create quiz: {str(e)}"}), 500



@admin_bp.route("/chapters/<int:chap_id>/quizzes", methods=["GET"])
@require_admin
@cache.cached(timeout=300, key_prefix=lambda: f"admin_quizzes_chapter_{request.view_args['chap_id']}")
def quizzes(chap_id):
    # Ensure chapter exists
    Chapter.query.get_or_404(chap_id)

    # Fetch all quizzes for the chapter
    quizzes = Quiz.query.filter_by(chapter_id=chap_id).all()
    return jsonify([
        {
            "id":           q.id,
            "name":         q.name,
            "description":  q.description,
            "deadline":     q.deadline.isoformat() if q.deadline else None,
            "duration":     str(q.duration),
            "remarks":      q.remarks
        }
        for q in quizzes
    ]), 200


@admin_bp.route("/quizzes/<int:id>", methods=["PUT", "DELETE"])
@require_admin
def modify_quiz(id):
    quiz = Quiz.query.get_or_404(id)

    if request.method == "PUT":
        try:
            data = request.get_json()
            print("📥 Incoming PUT payload:", data)

            name = data.get("name")
            description = data.get("description")
            duration_str = data.get("duration")
            deadline_str = data.get("deadline")
            remarks = data.get("remarks")

            if not name or not duration_str or not deadline_str:
                print("❌ Missing required fields")
                return jsonify({"error": "Name, duration, and deadline are required."}), 400

            # Parse duration
            h, m,s = map(int, duration_str.split(":"))
            quiz.duration = timedelta(hours=h, minutes=m, seconds=s)

            # Parse deadline
            quiz.deadline = datetime.strptime(deadline_str[:10], "%Y-%m-%d").date()

            quiz.name = name
            quiz.description = description
            quiz.remarks = remarks

            db.session.commit()
            # Invalidate caches
            cache.delete(f"admin_quiz_{id}")
            cache.delete(f"admin_quizzes_chapter_{quiz.chapter_id}")
            cache.delete("admin_quizzes_all")
            return jsonify(quiz.to_dict()), 200

        except Exception as e:
            return jsonify({"error": f"Exception during quiz update: {str(e)}"}), 400

    db.session.delete(quiz)
    db.session.commit()
    # Invalidate caches
    cache.delete(f"admin_quiz_{id}")
    cache.delete(f"admin_quizzes_chapter_{quiz.chapter_id}")
    cache.delete("admin_quizzes_all")
    return "", 204


# ------- Questions CRUD -------

@admin_bp.route("/questions", methods=["GET"])
@require_admin
@cache.cached(timeout=300, key_prefix="admin_all_questions")
@limiter.limit("15/minute")
def list_questions_global():
    """GET /api/admin/questions → returns every question"""
    questions = Question.query.all()
    return jsonify([
        {
            "id":                 q.id,
            "quiz_id":            q.quiz_id,
            "question_statement": q.question_statement,
            "option1":            q.option1,
            "option2":            q.option2,
            "option3":            q.option3,
            "option4":            q.option4,
            "correct_option":     q.correct_option
        }
        for q in questions
    ]), 200

@admin_bp.route("/quizzes/<int:quiz_id>/questions", methods=["GET"])
@require_admin
@cache.cached(
    timeout=300,
    key_prefix=lambda: f"admin_questions_quiz_{request.view_args['quiz_id']}"
)
def list_quiz_questions(quiz_id):
    Quiz.query.get_or_404(quiz_id)
    qs = Question.query.filter_by(quiz_id=quiz_id).all()
    return jsonify([
        {
            "id": q.id,
            "question_statement": q.question_statement,
            "option1": q.option1,
            "option2": q.option2,
            "option3": q.option3,
            "option4": q.option4,
            "correct_option": q.correct_option
        }
        for q in qs
    ]), 200

@admin_bp.route("/quizzes/<int:quiz_id>/questions", methods=["POST"])
@require_admin
def create_question(quiz_id):
    Quiz.query.get_or_404(quiz_id)
    data = request.get_json() or {}

    # Basic presence
    required = ["question_statement", "option1", "option2", "correct_option"]
    if any(not data.get(f) for f in required):
        return jsonify(msg="At least 2 options and question_statement are required"), 400

    # Trim and collect options
    opts = [data.get(f, "").strip() for f in ("option1","option2","option3","option4")]
    valid = [o for o in opts if o]
    if len(valid) < 2:
        return jsonify(msg="At least 2 valid options are required"), 400

    # Validate correct_option
    idx = data.get("correct_option")
    if not isinstance(idx, int) or idx < 1 or idx > len(valid):
        return jsonify(msg=f"Correct option must be between 1 and {len(valid)}"), 400

    # Create
    qn = Question(
        quiz_id=quiz_id,
        question_statement=data["question_statement"].strip(),
        option1=opts[0],
        option2=opts[1],
        option3=opts[2] if len(opts)>2 else "",
        option4=opts[3] if len(opts)>3 else "",
        correct_option=idx
    )
    db.session.add(qn)
    db.session.commit()

    # Bust the cache so your next GET sees it
    cache.delete(f"admin_questions_quiz_{quiz_id}")
    cache.delete("admin_all_questions")

    return jsonify(
        id=qn.id,
        question_statement=qn.question_statement,
        option1=qn.option1,
        option2=qn.option2,
        option3=qn.option3,
        option4=qn.option4,
        correct_option=qn.correct_option
    ), 201

@admin_bp.route("/questions/<int:id>", methods=["PUT", "DELETE"])
@require_admin
def modify_question(id):
    q = Question.query.get_or_404(id)

    if request.method == "PUT":
        data = request.get_json() or {}

        # Validate required fields
        if not data.get("question_statement") or not data.get("correct_option"):
            return jsonify(msg="question_statement and correct_option are required"), 400

        # Collect valid options
        options = []
        for i in range(1, 5):
            opt = data.get(f"option{i}", "").strip()
            if opt:
                options.append(opt)

        if len(options) < 2:
            return jsonify(msg="At least 2 options are required"), 400

        # Validate correct_option
        correct_index = data.get("correct_option")
        if not isinstance(correct_index, int) or correct_index < 1 or correct_index > len(options):
            return jsonify(msg=f"correct_option must be between 1 and {len(options)}"), 400

        # Update fields
        q.question_statement = data["question_statement"]
        q.correct_option = correct_index
        q.option1 = data.get("option1", "")
        q.option2 = data.get("option2", "")
        q.option3 = data.get("option3", "")
        q.option4 = data.get("option4", "")

        db.session.commit()
        cache.delete(f"admin_questions_quiz_{q.quiz_id}")
        cache.delete("admin_all_questions")

        return jsonify(
            id=q.id,
            question_statement=q.question_statement,
            option1=q.option1,
            option2=q.option2,
            option3=q.option3,
            option4=q.option4,
            correct_option=q.correct_option
        ), 200

    # DELETE
    db.session.delete(q)
    db.session.commit()
    cache.delete(f"admin_questions_quiz_{q.quiz_id}")
    cache.delete("admin_all_questions")
    return "", 204

# ------- List All Users -------

@admin_bp.route("/users", methods=["GET"])
@require_admin
@cache.cached(timeout=60 * 5, key_prefix="admin_user_list")
@limiter.limit("10 per minute")
def list_users():
    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "qualification": u.qualification,
            "dob": u.dob.isoformat() if u.dob else None,
            "is_admin": u.is_admin
        }
        for u in users
    ]), 200

@admin_bp.route("/recent-activity", methods=["GET"])
@require_admin
@cache.cached(timeout=60 * 2, key_prefix="admin_recent_activity")
@limiter.limit("5 per minute")
def recent_activity():
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
    return jsonify([
        {
            "type": log.type,
            "user": log.user,
            "message": log.message,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None
        }
        for log in logs
    ]), 200

# ------- User Details and Stats -------
@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@require_admin
@cache.cached(timeout=60 * 5, key_prefix=lambda: f"user_detail_{request.view_args['user_id']}")
@limiter.limit("5 per minute")
def get_user_by_id(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "qualification": user.qualification,
        "dob": user.dob.isoformat() if user.dob else None,
        "is_admin": user.is_admin
    }), 200

@admin_bp.route("/users/<int:user_id>/stats", methods=["GET"])
@require_admin
@cache.cached(timeout=60 * 5, key_prefix=lambda: f"user_stats_{request.view_args['user_id']}")
@limiter.limit("5 per minute")
def user_stats(user_id):
    user = User.query.get_or_404(user_id)
    scores = Score.query.filter_by(user_id=user_id).all()
    total = len(scores)
    avg = round(sum(s.total_score for s in scores) / total, 2) if total else 0
    last = max((s.timestamp for s in scores), default=None)
    return jsonify({
        "totalQuizzes": total,
        "avgScore": avg,
        "lastActive": last.isoformat() if last else None
    }), 200

@admin_bp.route("/users/<int:user_id>/activity", methods=["GET"])
@require_admin
@cache.cached(timeout=60 * 5, key_prefix=lambda: f"user_activity_{request.view_args['user_id']}")
@limiter.limit("5 per minute")
def user_activity(user_id):
    scores = Score.query.filter_by(user_id=user_id).order_by(Score.timestamp.desc()).limit(10).all()
    return jsonify([
        {
            "quiz": s.quiz.id,
            "subject": s.quiz.chapter.subject.name,
            "score": s.total_score,
            "accuracy": s.accuracy,
            "completed_at": s.timestamp.isoformat()
        } for s in scores
    ]), 200

@admin_bp.route("/me", methods=["GET", "OPTIONS"])
def get_admin_me():
    if request.method == "OPTIONS":
        return '', 200  
    
    verify_jwt_in_request()

    # 🔒 Ensure user is an admin
    claims = get_jwt()
    if not claims.get("is_admin"):
        return jsonify(msg="Admins only"), 403

    admin_id = int(get_jwt_identity())
    admin = User.query.get_or_404(admin_id)
    return jsonify({
        "name": admin.full_name,
        "email": admin.email,
        "qualification": admin.qualification
    }), 200

def make_subject_cache_key():
    return f"subject_detail_{request.view_args['id']}"

@admin_bp.route("/subjects/<int:id>", methods=["GET"])
@require_admin
@limiter.limit("5 per minute")
@cache.cached(timeout=300, key_prefix=make_subject_cache_key)
def get_subject_by_id(id):
    subject = Subject.query.get_or_404(id)
    return jsonify({
        "id": subject.id,
        "name": subject.name,
        "description": subject.description
    }), 200

@admin_bp.route("/chapters/<int:id>", methods=["GET"])
@require_admin
@cache.cached(timeout=60 * 5, key_prefix=lambda: f"chapter_detail_{request.view_args['id']}")
@limiter.limit("5 per minute")
def get_chapter_by_id(id):
    chapter = Chapter.query.get_or_404(id)
    quizzes = Quiz.query.filter_by(chapter_id=id).all()

    return jsonify({
        "id": chapter.id,
        "name": chapter.name,
        "description": chapter.description,
        "subject_id": chapter.subject_id,
        "quizCount": len(quizzes),
        "quizzes": [
            {
                "id": q.id,
                "name": q.name,
                "duration": str(q.duration),
                "deadline": q.deadline,
            } for q in quizzes
        ]
    }), 200
