from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.budget import Budget
from sqlalchemy import func
from datetime import datetime
from dateutil.relativedelta import relativedelta

main = Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def index():
    if current_user.is_authenticated:
        return dashboard()
    return render_template('main/landing.html', title='MoneyTracker')

@main.route('/dashboard')
@login_required
def dashboard():
    now   = datetime.now()
    month = now.month
    year  = now.year

    def monthly_sum(type_, m=None, y=None):
        m = m or month
        y = y or year
        return float(
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.user_id == current_user.id,
                Transaction.type    == type_,
                func.extract('month', Transaction.date) == m,
                func.extract('year',  Transaction.date) == y,
            ).scalar()
        )

    income       = monthly_sum('income')
    expense      = monthly_sum('expense')
    balance      = income - expense
    savings_rate = round((balance / income * 100), 1) if income > 0 else 0

    # All time stats
    total_income = float(
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter_by(user_id=current_user.id, type='income').scalar()
    )
    total_expense = float(
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter_by(user_id=current_user.id, type='expense').scalar()
    )
    total_tx = Transaction.query.filter_by(user_id=current_user.id).count()

    recent = (Transaction.query
              .filter_by(user_id=current_user.id)
              .order_by(Transaction.date.desc())
              .limit(5).all())

    cat_expense = (
        db.session.query(Category.name, Category.icon,
                         func.coalesce(func.sum(Transaction.amount), 0))
        .outerjoin(Transaction,
                   (Transaction.category_id == Category.id) &
                   (Transaction.type == 'expense') &
                   (func.extract('month', Transaction.date) == month) &
                   (func.extract('year',  Transaction.date) == year))
        .filter(Category.user_id == current_user.id, Category.type == 'expense')
        .group_by(Category.id)
        .having(func.sum(Transaction.amount) > 0)
        .all()
    )

    top_categories = sorted(cat_expense, key=lambda x: x[2], reverse=True)[:3]

    # Bar chart 6 เดือนย้อนหลัง
    bar_labels, bar_income, bar_expense = [], [], []
    for i in range(5, -1, -1):
        d = now - relativedelta(months=i)
        bar_labels.append(d.strftime('%b %y'))
        bar_income.append(monthly_sum('income',  d.month, d.year))
        bar_expense.append(monthly_sum('expense', d.month, d.year))

    # Budget progress
    budgets = Budget.query.filter_by(
        user_id=current_user.id, month=month, year=year).limit(4).all()
    budget_data = []
    for b in budgets:
        spent = float(
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.user_id     == current_user.id,
                Transaction.category_id == b.category_id,
                Transaction.type        == 'expense',
                func.extract('month', Transaction.date) == month,
                func.extract('year',  Transaction.date) == year,
            ).scalar()
        )
        limit = float(b.amount)
        budget_data.append({
            'budget': b, 'spent': spent, 'limit': limit,
            'pct': min(int(spent / limit * 100), 100) if limit else 0,
        })

    return render_template('main/dashboard.html',
        title='Dashboard',
        income=income, expense=expense, balance=balance,
        savings_rate=savings_rate,
        total_income=total_income, total_expense=total_expense,
        total_tx=total_tx,
        recent=recent,
        cat_labels=[f"{r[1]} {r[0]}" for r in cat_expense],
        cat_values=[float(r[2]) for r in cat_expense],
        top_categories=top_categories,
        bar_labels=bar_labels, bar_income=bar_income, bar_expense=bar_expense,
        budget_data=budget_data,
    )