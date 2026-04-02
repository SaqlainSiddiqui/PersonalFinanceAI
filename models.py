from extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(200))
    theme_mode = db.Column(db.String(10), default="light")

    transactions = db.relationship("Transaction", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    amount = db.Column(db.Float)
    category = db.Column(db.String(100))
    type = db.Column(db.String(10))
    date = db.Column(db.Date, default=datetime.utcnow)
    description = db.Column(db.String(200))
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_type = db.Column(db.String(20))  # monthly / weekly
    last_generated = db.Column(db.Date)
    