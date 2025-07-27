# tasks/export.py

import csv
import io
import pytz
from flask_mail import Message
from extensions import mail, db
from models import Score, User, Quiz, Chapter, Subject
from celery_app import celery
from app import create_app

@celery.task(name="tasks.export.export_quiz_history_task")
def export_quiz_history_task(user_id):
    app = create_app()

    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "❌ User not found"

        scores = (
            Score.query
            .filter_by(user_id=user_id)
            .order_by(Score.timestamp.desc())
            .all()
        )

        if not scores:
            return "❌ No quiz history available"

        # Prepare CSV in-memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Quiz Title", "Score", "Accuracy", "Completed At"])

        for score in scores:
            quiz = Quiz.query.get(score.quiz_id)
            if not quiz:
                continue

            chapter = Chapter.query.get(quiz.chapter_id)
            subject = Subject.query.get(chapter.subject_id)
            total_questions = len(quiz.questions)

            accuracy = round((score.total_score / total_questions) * 100, 2) if total_questions else 0

            # ✅ Correct UTC to IST conversion
            timestamp_utc = pytz.utc.localize(score.timestamp)
            timestamp_ist = timestamp_utc.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %I:%M %p IST")

            writer.writerow([
                f"{subject.name} / {chapter.name} / {quiz.name}",
                f'"{score.total_score} / {total_questions}"',
                f'"{accuracy}%"',
                timestamp_ist
            ])

        # Prepare email
        output.seek(0)
        msg = Message(
            subject="📊 Your Quiz History Report",
            recipients=[user.email],
            body=f"Hi {user.full_name},\n\nAttached is your quiz history report in CSV format.\n\nRegards,\nQuizzy Team"
        )
        msg.attach("quiz_history.csv", "text/csv", output.read())

        try:
            mail.send(msg)
            return "✅ CSV emailed successfully"
        except Exception as e:
            return f"❌ Failed to send email: {str(e)}"
