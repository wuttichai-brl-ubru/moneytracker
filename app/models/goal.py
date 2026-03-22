from app.extensions import db
from datetime import datetime

class Goal(db.Model):
    __tablename__ = 'goal'

    id           = db.Column(db.Integer,       primary_key=True)
    name         = db.Column(db.String(150),   nullable=False)
    icon         = db.Column(db.String(10),    default='🎯')
    target_amount= db.Column(db.Numeric(12,2), nullable=False)
    saved_amount = db.Column(db.Numeric(12,2), default=0)
    deadline     = db.Column(db.Date,          nullable=True)
    note         = db.Column(db.String(255))
    created_at   = db.Column(db.DateTime,      default=datetime.utcnow)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def pct(self):
        if self.target_amount and float(self.target_amount) > 0:
            return min(int(float(self.saved_amount) / float(self.target_amount) * 100), 100)
        return 0

    @property
    def remaining(self):
        return max(float(self.target_amount) - float(self.saved_amount), 0)

    def __repr__(self):
        return f'<Goal {self.name}>'