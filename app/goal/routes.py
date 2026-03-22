from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.goal.forms import GoalForm
from app.models.goal import Goal

goal = Blueprint('goal', __name__, template_folder='templates')

@goal.route('/')
@login_required
def index():
    goals = Goal.query.filter_by(user_id=current_user.id)\
                .order_by(Goal.created_at.desc()).all()
    return render_template('goal/goal_list.html', title='Savings Goals', goals=goals)

@goal.route('/add', methods=['GET', 'POST'])
@login_required
def add_goal():
    form = GoalForm()
    if form.validate_on_submit():
        g = Goal(
            icon=form.icon.data,
            name=form.name.data,
            target_amount=form.target_amount.data,
            saved_amount=form.saved_amount.data or 0,
            deadline=form.deadline.data,
            note=form.note.data,
            user_id=current_user.id,
        )
        db.session.add(g)
        db.session.commit()
        flash(f'Goal "{g.name}" created! 🎯', 'success')
        return redirect(url_for('goal.index'))
    return render_template('goal/goal_form.html',
        form=form, title='Add Goal', is_edit=False)

@goal.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_goal(id):
    g    = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = GoalForm(obj=g)
    if form.validate_on_submit():
        g.icon          = form.icon.data
        g.name          = form.name.data
        g.target_amount = form.target_amount.data
        g.saved_amount  = form.saved_amount.data or 0
        g.deadline      = form.deadline.data
        g.note          = form.note.data
        db.session.commit()
        flash('Goal updated! ✅', 'success')
        return redirect(url_for('goal.index'))
    return render_template('goal/goal_form.html',
        form=form, title='Edit Goal', is_edit=True, goal=g)

@goal.route('/deposit/<int:id>', methods=['POST'])
@login_required
def deposit(id):
    g      = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    amount = float(request.form.get('amount', 0))
    if amount > 0:
        g.saved_amount = float(g.saved_amount) + amount
        db.session.commit()
        flash(f'Added ฿{amount:,.2f} to "{g.name}"! 💰', 'success')
    return redirect(url_for('goal.index'))

@goal.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_goal(id):
    g = Goal.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(g)
    db.session.commit()
    flash('Goal deleted.', 'warning')
    return redirect(url_for('goal.index'))