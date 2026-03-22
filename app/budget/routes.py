from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.budget.forms import BudgetForm
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction
from sqlalchemy import func
from datetime import datetime

budget = Blueprint('budget', __name__, template_folder='templates')

@budget.route('/')
@login_required
def index():
    now   = datetime.utcnow()
    month = request.args.get('month', now.month, type=int)
    year  = request.args.get('year',  now.year,  type=int)

    budgets = Budget.query.filter_by(
        user_id=current_user.id, month=month, year=year).all()

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
            'budget': b,
            'spent':  spent,
            'limit':  limit,
            'pct':    min(int(spent / limit * 100), 100) if limit else 0,
        })

    return render_template('budget/budget_list.html',
        title='Budget', budget_data=budget_data,
        month=month, year=year)

@budget.route('/add', methods=['GET', 'POST'])
@login_required
def add_budget():
    form = BudgetForm()
    form.category_id.choices = [
        (c.id, f"{c.icon} {c.name}")
        for c in Category.query.filter_by(
            user_id=current_user.id, type='expense').all()
    ]
    if form.validate_on_submit():
        exists = Budget.query.filter_by(
            user_id=current_user.id, category_id=form.category_id.data,
            month=form.month.data, year=form.year.data).first()
        if exists:
            flash('A budget for this category already exists this month.', 'warning')
            return redirect(url_for('budget.index'))
        b = Budget(
            amount=form.amount.data,           month=form.month.data,
            year=form.year.data,               category_id=form.category_id.data,
            user_id=current_user.id,
        )
        db.session.add(b)
        db.session.commit()
        flash('Budget set! ✅', 'success')
        return redirect(url_for('budget.index'))
    return render_template('budget/budget_form.html',
        form=form, title='Set Budget', is_edit=False)

@budget.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_budget(id):
    b    = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = BudgetForm(obj=b)
    form.category_id.choices = [
        (c.id, f"{c.icon} {c.name}")
        for c in Category.query.filter_by(
            user_id=current_user.id, type='expense').all()
    ]
    if form.validate_on_submit():
        b.amount      = form.amount.data
        b.month       = form.month.data
        b.year        = form.year.data
        b.category_id = form.category_id.data
        db.session.commit()
        flash('Budget updated! ✅', 'success')
        return redirect(url_for('budget.index'))
    return render_template('budget/budget_form.html',
        form=form, title='Edit Budget', is_edit=True, budget_item=b)

@budget.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_budget(id):
    b = Budget.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(b)
    db.session.commit()
    flash('Budget deleted.', 'warning')
    return redirect(url_for('budget.index'))