from app.extensions import db, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id            = db.Column(db.Integer,     primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    fullname      = db.Column(db.String(150), nullable=True)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), default='avatar.png')
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)

    categories   = db.relationship('Category',    backref='owner', lazy=True,
                                   cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='owner', lazy=True,
                                   cascade='all, delete-orphan')
    budgets      = db.relationship('Budget',      backref='owner', lazy=True,
                                   cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def display_name(self):
        return self.fullname if self.fullname else self.username

    def __repr__(self):
        return f'<User {self.username}>'