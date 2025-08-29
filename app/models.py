from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=False)
    start_nr = db.Column(db.Integer, nullable=True, unique=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    photo = db.Column(db.String(256), nullable=True)
    time1 = db.Column(db.Float, nullable=True)
    time2 = db.Column(db.Float, nullable=True)
    time3 = db.Column(db.Float, nullable=True)
    time4 = db.Column(db.Float, nullable=True)
    time5 = db.Column(db.Float, nullable=True)
    time6 = db.Column(db.Float, nullable=True)
    round1_qualified = db.Column(db.Boolean, default=False)
    round2_qualified = db.Column(db.Boolean, default=False)
    round3_qualified = db.Column(db.Boolean, default=False)
    zwischenrunde_qualified = db.Column(db.Boolean, default=False)
    final_qualified = db.Column(db.Boolean, default=False)

    @property
    def toptime_Vorrunde(self):
        times = [t for t in [self.time1, self.time2, self.time3] if t is not None]
        return max(times) if times else None

    @property
    def toptime_Zwischenrunde(self):
        times = [t for t in [self.time4, self.time5] if t is not None]
        return max(times) if times else None

    @property
    def toptime_Finalrunde(self):
        times = [t for t in [self.time6] if t is not None]
        return max(times) if times else None
