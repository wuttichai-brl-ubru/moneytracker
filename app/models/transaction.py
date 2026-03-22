from app.extensions import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transaction'

    id          = db.Column(db.Integer,       primary_key=True)
    amount      = db.Column(db.Numeric(12,2), nullable=False)
    description = db.Column(db.String(255))
    type        = db.Column(db.String(10),    nullable=False)
    date        = db.Column(db.DateTime,      nullable=False, default=datetime.now)  # ← DateTime
    slip_image  = db.Column(db.String(255))
    created_at  = db.Column(db.DateTime,      default=datetime.now)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'),     nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f'<Transaction {self.amount} ({self.type})>'