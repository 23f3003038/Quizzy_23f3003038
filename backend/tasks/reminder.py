import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date, datetime, timedelta
from flask_mail import Message
from extensions import mail, db
from models import User, Quiz, Score
from app import create_app
from celery_app import celery


@celery.task(name='tasks.reminder.send_daily_quiz_reminders')
def send_daily_quiz_reminders():
    app = create_app()
    with app.app_context():
        users = User.query.filter_by(is_admin=False).all()

        today = date.today()

        reminders_sent = 0

        for user in users:
            if not user.email:
                continue  # Skip if user has no email

            pending_quizzes = Quiz.query.filter(Quiz.deadline >= today).all()

            if not pending_quizzes:
                continue

            msg = Message(
                subject="📚 Daily Quiz Reminder - Quizzy",
                recipients=[user.email],
                body=f"""Hi {user.full_name or 'User'},\n
You have {len(pending_quizzes)} quizzes pending with deadlines starting from today.

Stay on track and keep learning!

- Team Quizzy"""
            )
            try:
                mail.send(msg)
                reminders_sent += 1
            except Exception as e:
                print(f"❌ Failed to send daily reminder to {user.email}: {e}")

        return f"✅ Sent reminders to {len(users)} user{'s' if len(users) != 1 else ''}"


@celery.task(name='tasks.reminder.send_monthly_reports')
def send_monthly_reports():
    app = create_app()
    with app.app_context():
        today = datetime.today()
        start_date = today.replace(day=1)
        last_month = start_date - timedelta(days=1)
        from_date = last_month.replace(day=1)
        to_date = last_month

        reports_sent = 0
        users = User.query.filter_by(is_admin=False).all()

        for user in users:
            if not user.email:
                continue  # Skip if user has no email

            scores = (
                Score.query
                .filter(
                    Score.user_id == user.id,
                    Score.timestamp >= from_date,
                    Score.timestamp <= to_date
                )
                .all()
            )

            if not scores:
                print(f"⚠️ No quiz data for {user.email} in {from_date.strftime('%B')}. Skipping.")
                continue

            total = len(scores)
            avg_score = sum(score.total_score or 0 for score in scores) / total

            msg = Message(
                subject=f"📈 Monthly Performance Report - {from_date.strftime('%B %Y')}",
                recipients=[user.email],
                body=f"""Hi {user.full_name or 'User'},\n
Here's your performance for {from_date.strftime('%B %Y')}:

📊 Quizzes Attempted: {total}
🎯 Average Score: {round(avg_score, 2)}

Keep it up!

- Team Quizzy"""
            )
            try:
                mail.send(msg)
                reports_sent += 1
            except Exception as e:
                print(f"❌ Failed to send monthly report to {user.email}: {e}")

        if reports_sent == 0:
            return "⚠️ No reports sent — no eligible user data or email failure."
        return f"✅ Sent {reports_sent} monthly report{'s' if reports_sent > 1 else ''}"
