from datetime import datetime, timedelta
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100))
    dob = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)

    scores = db.relationship(
        "Score", back_populates="user", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "qualification": self.qualification,
            "dob": self.dob.isoformat() if self.dob else None,
            "is_admin": self.is_admin,
        }

    @property
    def password(self):
        raise AttributeError("Use set_password() to set the user password.")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    chapters = db.relationship(
        "Chapter", back_populates="subject", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class Chapter(db.Model):
    __tablename__ = "chapters"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    name = db.Column(db.String(100), unique= True, nullable=False)
    description = db.Column(db.Text)

    subject = db.relationship("Subject", back_populates="chapters")
    quizzes = db.relationship(
        "Quiz", back_populates="chapter", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "subject_id": self.subject_id,
            "name": self.name,
            "description": self.description,
        }


class Quiz(db.Model):
    __tablename__ = "quizzes"

    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapters.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Interval, default=timedelta(minutes=0), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deadline = db.Column(db.DateTime, nullable=False)
    remarks = db.Column(db.Text)

    chapter = db.relationship("Chapter", back_populates="quizzes")
    questions = db.relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    scores = db.relationship("Score", back_populates="quiz", cascade="all, delete-orphan")

    def to_dict(self, include_questions=False, include_scores=False):
        data = {
            "id": self.id,
            "chapter_id": self.chapter_id,
            "name": self.name,
            "description": self.description,
            "duration": str(self.duration),
            "deadline": self.deadline.strftime("%Y-%m-%d") if self.deadline else None,
            "remarks": self.remarks,
        }
        if include_questions:
            data["questions"] = [q.to_dict() for q in self.questions]
        if include_scores:
            data["scores"] = [s.to_dict() for s in self.scores]
        return data


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(255), nullable=False)
    option2 = db.Column(db.String(255), nullable=False)
    option3 = db.Column(db.String(255), nullable=False)
    option4 = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)

    quiz = db.relationship("Quiz", back_populates="questions")

    def to_dict(self):
        return {
            "id": self.id,
            "quiz_id": self.quiz_id,
            "question_statement": self.question_statement,
            "option1": self.option1,
            "option2": self.option2,
            "option3": self.option3,
            "option4": self.option4,
            "correct_option": self.correct_option,
        }


class Score(db.Model):
    __tablename__ = "scores"

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_score = db.Column(db.Integer)

    quiz = db.relationship("Quiz", back_populates="scores")
    user = db.relationship("User", back_populates="scores")
    answers = db.relationship("UserAnswer", back_populates="score", cascade="all, delete-orphan", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "quiz_id": self.quiz_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "total_score": self.total_score,
        }


class UserAnswer(db.Model):
    __tablename__ = "user_answers"

    id = db.Column(db.Integer, primary_key=True)
    score_id = db.Column(db.Integer, db.ForeignKey("scores.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    selected = db.Column(db.Integer, nullable=True)

    score = db.relationship("Score", back_populates="answers")
    question = db.relationship("Question")


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    user = db.Column(db.String(120), nullable=True)
    quiz = db.Column(db.String(120), nullable=True)
    quiz_name = db.Column(db.String(255), nullable=True)
    admin = db.Column(db.String(120), nullable=True)
    message = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "type": self.type,
            "user": self.user,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
