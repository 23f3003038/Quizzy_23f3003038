# backend/routes/user.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Quiz, Question, Score
from datetime import datetime

user_bp = Blueprint("user", __name__)

@user_bp.route("/quizzes", methods=["GET"])
@jwt_required()
def list_quizzes():
    """
    List all quizzes (for any authenticated user).
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
    Expects JSON body: { "answers": [ {"question_id": 1, "selected": 2}, ... ] }
    """
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    answers = data.get("answers", [])

    # Calculate total correct
    total_correct = 0
    for ans in answers:
        q = Question.query.get(ans.get("question_id"))
        if q and q.correct_option == ans.get("selected"):
            total_correct += 1

    # Record the score
    score = Score(
        quiz_id=quiz_id,
        user_id=user_id,
        timestamp=datetime.utcnow(),
        total_score=total_correct
    )
    db.session.add(score)
    db.session.commit()

    return jsonify(
        quiz_id=quiz_id,
        user_id=user_id,
        total_score=total_correct
    ), 201

@user_bp.route("/scores", methods=["GET"])
@jwt_required()
def get_my_scores():
    """
    Get the authenticated user's past quiz attempts and scores.
    """
    user_id = get_jwt_identity()
    scores = Score.query.filter_by(user_id=user_id).order_by(Score.timestamp.desc()).all()
    return jsonify([
        {
            "quiz_id": s.quiz_id,
            "timestamp": s.timestamp.isoformat(),
            "total_score": s.total_score
        }
        for s in scores
    ]), 200
