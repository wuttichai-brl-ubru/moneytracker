from app.extensions import db

class Category(db.Model):
    __tablename__ = 'category'

    id      = db.Column(db.Integer,     primary_key=True)
    name    = db.Column(db.String(100), nullable=False)
    type    = db.Column(db.String(10),  nullable=False)  # 'income' | 'expense'
    icon    = db.Column(db.String(10),  default='💰')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    transactions = db.relationship('Transaction', backref='category', lazy=True)
    budgets      = db.relationship('Budget',      backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'