from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.transaction.forms import TransactionForm
from app.models.transaction import Transaction
from app.models.category import Category
from PIL import Image
import os, secrets

transaction = Blueprint('transaction', __name__, template_folder='templates')

def save_slip(file):
    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = f"slip_{secrets.token_hex(8)}.{ext}"
    path     = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    img      = Image.open(file)
    img.thumbnail((1000, 1000))
    img.save(path)
    return filename

def category_choices():
    cats = Category.query.filter_by(user_id=current_user.id).all()
    return [(c.id, f"{c.icon} {c.name}", c.type) for c in cats]   # ← เพิ่ม c.type

@transaction.route('/')
@login_required
def index():
    page        = request.args.get('page', 1, type=int)
    search      = request.args.get('search', '').strip()
    type_filter = request.args.get('type', '')

    q = Transaction.query.filter_by(user_id=current_user.id)
    if search:
        q = q.filter(Transaction.description.ilike(f'%{search}%'))
    if type_filter in ('income', 'expense'):
        q = q.filter_by(type=type_filter)

    paginated = (q.order_by(Transaction.date.desc(), Transaction.created_at.desc())
                  .paginate(page=page, per_page=10, error_out=False))

    return render_template('transaction/transaction_list.html',
        title='Transactions',
        transactions=paginated,
        search=search, type_filter=type_filter)

@transaction.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form    = TransactionForm()
    choices = category_choices()
    form.category_id.choices = [(c[0], c[1]) for c in choices]   # ← แก้
    if form.validate_on_submit():
        slip = save_slip(form.slip_image.data) if form.slip_image.data else None
        t = Transaction(
            amount=form.amount.data,           type=form.type.data,
            category_id=form.category_id.data, description=form.description.data,
            date=form.date.data,               slip_image=slip,
            user_id=current_user.id,
        )
        db.session.add(t)
        db.session.commit()
        flash('Transaction saved! ✅', 'success')
        return redirect(url_for('transaction.index'))
    return render_template('transaction/transaction_form.html',
        form=form, title='Add Transaction', is_edit=False,
        category_types={ c[0]: c[2] for c in choices })   # ← เพิ่ม

@transaction.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    t       = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form    = TransactionForm(obj=t)
    choices = category_choices()
    form.category_id.choices = [(c[0], c[1]) for c in choices]   # ← แก้
    if form.validate_on_submit():
        if form.slip_image.data:
            t.slip_image = save_slip(form.slip_image.data)
        t.amount      = form.amount.data
        t.type        = form.type.data
        t.category_id = form.category_id.data
        t.description = form.description.data
        t.date        = form.date.data
        db.session.commit()
        flash('Transaction updated! ✅', 'success')
        return redirect(url_for('transaction.index'))
    return render_template('transaction/transaction_form.html',
        form=form, title='Edit Transaction', is_edit=True, transaction=t,
        category_types={ c[0]: c[2] for c in choices })   # ← เพิ่ม

@transaction.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_transaction(id):
    t = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(t)
    db.session.commit()
    flash('Transaction deleted.', 'warning')
    return redirect(url_for('transaction.index'))