# backend/routes/user.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app import db
from models import User, Subject, Chapter, Quiz, Question, Score

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

@user_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_user_dashboard():
    """
    Return user profile info and quiz stats for dashboard.
    """
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    # Fetch quiz scores
    scores = Score.query.filter_by(user_id=user_id).all()
    total_quizzes = len(scores)
    total_score = sum([s.total_score for s in scores])
    max_score_per_quiz = 10  # adjust this if your quiz max score is different

    average_score = round((total_score / (total_quizzes * max_score_per_quiz)) * 100, 2) if total_quizzes else 0
    accuracy = average_score  # if accuracy is based on total score

    last_active = max([s.timestamp for s in scores], default=None)

    return jsonify({
        "full_name": user.full_name,
        "email": user.email,
        "student_id": user.id,
        "qualification": user.qualification,
        "dob": user.dob.isoformat() if user.dob else None,
        "total_quizzes": total_quizzes,
        "average_score": average_score,
        "accuracy": accuracy,
        "last_active": last_active.isoformat() if last_active else None
    }), 200

@user_bp.route("/subjects", methods=["GET"])
@jwt_required()
def list_subjects():
    """
    List all subjects (for authenticated users).
    """
    subjects = Subject.query.all()
    return jsonify([
        {
            "id": s.id,
            "name": s.name,
            "description": s.description
        }
        for s in subjects
    ]), 200

@user_bp.route("/subjects/<int:subject_id>", methods=["GET"])
@jwt_required()
def get_subject_by_id(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return jsonify({
        "id": subject.id,
        "name": subject.name,
        "description": subject.description
    }), 200

@user_bp.route("/subjects/<int:subject_id>/chapters", methods=["GET"])
@jwt_required()
def get_chapters_by_subject(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()

    chapter_data = []
    for chapter in chapters:
        quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
        chapter_data.append({
            "id": chapter.id,
            "name": chapter.name,
            "description": chapter.description,
            "quizzes": [{"id": q.id, "remarks": q.remarks} for q in quizzes]
        })

    return jsonify(chapter_data), 200

@user_bp.route("/subjects/<int:subject_id>/quizzes", methods=["GET"])
@jwt_required()
def list_quizzes_by_subject(subject_id):
    """
    List all quizzes for a given subject.
    """
    # Join through Chapter to filter by subject
    quizzes = (
        Quiz.query
        .join(Chapter, Quiz.chapter_id == Chapter.id)
        .filter(Chapter.subject_id == subject_id)
        .all()
    )
    return jsonify([
        {
            "id": q.id,
            "chapter_id": q.chapter_id,
            "date_of_quiz": q.date_of_quiz.isoformat(),
            "duration_minutes": int(q.duration.total_seconds() // 60),
            "remarks": q.remarks
        }
        for q in quizzes
    ]), 200

@user_bp.route("/chapters/<int:chapter_id>", methods=["GET"])
@jwt_required()
def get_chapter_details(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)

    return jsonify({
        "subject_id": chapter.subject_id,
        "id": chapter.id,
        "name": chapter.name,
        "description": chapter.description,
        "quizzes": [
            {
                "id": q.id,
                "deadline": q.deadline.isoformat(),
                "duration_minutes": int(q.duration.total_seconds() // 60),
                "remarks": q.remarks
            } for q in chapter.quizzes
        ]
    }), 200

@user_bp.route("/quizzes", methods=["GET"])
@jwt_required()
def list_all_quizzes():
    """
    List all quizzes across all subjects (for authenticated users).
    """
    quizzes = Quiz.query.all()
    return jsonify([
        {
            "id": q.id,
            "chapter_id": q.chapter_id,
            "date_of_quiz": q.date_of_quiz.isoformat(),
            "duration_minutes": int(q.duration.total_seconds() // 60),
            "remarks": q.remarks
        }
        for q in quizzes
    ]), 200

@user_bp.route("/quizzes/<int:quiz_id>", methods=["GET"])

def get_quiz_by_id(quiz_id):
    """
    Get details of a specific quiz including optional question list.
    """
    quiz = Quiz.query.get_or_404(quiz_id)

    return jsonify({
        "id": quiz.id,
        "chapter_id": quiz.chapter_id,
        "name": quiz.name,
        "description": quiz.description,
        "duration": str(quiz.duration),
        "deadline": quiz.deadline.isoformat() if quiz.deadline else None,
        "remarks": quiz.remarks,
        "questions": [q.to_dict() for q in quiz.questions]
    }), 200

@user_bp.route("/quizzes/<int:quiz_id>/questions", methods=["GET"])
@jwt_required()
def get_quiz_questions(quiz_id):
    """
    Get all questions (and options) for a given quiz.
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify([
        {
            "question_id": q.id,
            "question_statement": q.question_statement,
            "options": [q.option1, q.option2, q.option3, q.option4]
        }
        for q in quiz.questions
    ]), 200

@user_bp.route("/quizzes/<int:quiz_id>/submit", methods=["POST"])
@jwt_required()
def submit_quiz(quiz_id):
    """
    Submit answers for a quiz and record the score.
    Expects JSON body:
      { "answers": [ {"question_id": 1, "selected": 2}, ... ] }
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    answers = data.get("answers", [])

    total_correct = 0
    detailed_results = []

    for ans in answers:
        q = Question.query.get(ans.get("question_id"))
        if q:
            is_correct = q.correct_option == ans.get("selected")
            if is_correct:
                total_correct += 1

            detailed_results.append({
                "question_id": q.id,
                "question_statement": q.question_statement,
                "options": [q.option1, q.option2, q.option3, q.option4],
                "selected": ans.get("selected"),
                "correct_option": q.correct_option,
                "is_correct": is_correct
            })

    # Record the score
    score = Score(
        quiz_id=quiz_id,
        user_id=user_id,
        timestamp=datetime.utcnow(),
        total_score=total_correct
    )
    db.session.add(score)
    db.session.commit()

    return jsonify({
        "quiz_id": quiz_id,
        "user_id": user_id,
        "total_score": total_correct,
        "total_questions": len(answers),
        "questions": detailed_results
    }), 201

@user_bp.route("/quizzes/<int:quiz_id>/result", methods=["GET"])
@jwt_required()
def get_quiz_result(quiz_id):
    """
    Get detailed result of the quiz attempt by the current user.
    Returns score, total questions, and answer breakdown.
    """
    user_id = get_jwt_identity()

    # Get the latest score record
    score = (
        Score.query
        .filter_by(user_id=user_id, quiz_id=quiz_id)
        .order_by(Score.timestamp.desc())
        .first()
    )

    if not score:
        return jsonify({"error": "No attempt found for this quiz."}), 404

    quiz = Quiz.query.get_or_404(quiz_id)

    detailed_results = []
    for q in quiz.questions:
        selected_answer = next((
            ans.selected for ans in score.answers if ans.question_id == q.id
        ), None) if hasattr(score, 'answers') else None

        detailed_results.append({
            "question_id": q.id,
            "question_statement": q.question_statement,
            "options": [q.option1, q.option2, q.option3, q.option4],
            "selected": selected_answer,
            "correct_option": q.correct_option,
            "is_correct": selected_answer == q.correct_option
        })

    return jsonify({
        "quiz_id": quiz_id,
        "user_id": user_id,
        "total_score": score.total_score,
        "total_questions": len(quiz.questions),
        "questions": detailed_results
    }), 200

@user_bp.route("/scores", methods=["GET"])
@jwt_required()
def get_my_scores():
    """
    Get the authenticated user's past quiz attempts and scores.
    """
    user_id = get_jwt_identity()
    scores = (
        Score.query
        .filter_by(user_id=user_id)
        .order_by(Score.timestamp.desc())
        .all()
    )
    return jsonify([
        {
            "quiz_id": s.quiz_id,
            "timestamp": s.timestamp.isoformat(),
            "total_score": s.total_score
        }
        for s in scores
    ]), 200
