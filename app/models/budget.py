from app.extensions import db

class Budget(db.Model):
    __tablename__ = 'budget'

    id          = db.Column(db.Integer,       primary_key=True)
    amount      = db.Column(db.Numeric(12,2), nullable=False)
    month       = db.Column(db.Integer,       nullable=False)  # 1–12
    year        = db.Column(db.Integer,       nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'),     nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f'<Budget {self.amount} {self.month}/{self.year}>'