from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models.transaction import Transaction
from app.models.category import Category
from sqlalchemy import func
from datetime import datetime

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
@login_required
def index():
    now   = datetime.utcnow()
    month = now.month
    year  = now.year

    def monthly_sum(type_):
        return float(
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.type    == type_,
                func.extract('month', Transaction.date) == month,
                func.extract('year',  Transaction.date) == year,
            ).scalar()
        )

    income  = monthly_sum('income')
    expense = monthly_sum('expense')
    balance = income - expense

    recent = (Transaction.query
              .filter_by(user_id=current_user.id)
              .order_by(Transaction.date.desc(), Transaction.created_at.desc())
              .limit(5).all())

    cat_expense = (
        db.session.query(
            Category.name, Category.icon,
            func.coalesce(func.sum(Transaction.amount), 0)
        )
        .outerjoin(Transaction,
                   (Transaction.category_id == Category.id) &
                   (Transaction.type == 'expense') &
                   (func.extract('month', Transaction.date) == month) &
                   (func.extract('year',  Transaction.date) == year))
        .filter(Category.user_id == current_user.id,
                Category.type    == 'expense')
        .group_by(Category.id)
        .having(func.sum(Transaction.amount) > 0)
        .all()
    )

    return render_template('main/dashboard.html',
        title='Dashboard',
        income=income, expense=expense, balance=balance,
        recent=recent,
        cat_labels=[f"{r[1]} {r[0]}" for r in cat_expense],
        cat_values=[float(r[2])       for r in cat_expense],
    )