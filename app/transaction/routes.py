from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, Response
from flask_login import login_required, current_user
from app.extensions import db
from app.transaction.forms import TransactionForm
from app.models.transaction import Transaction
from app.models.category import Category
from PIL import Image
from sqlalchemy import extract
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os, secrets, csv, io, json

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
    return [(c.id, f"{c.icon} {c.name}", c.type) for c in cats]

@transaction.route('/')
@login_required
def index():
    page        = request.args.get('page',   1,  type=int)
    search      = request.args.get('search', '').strip()
    type_filter = request.args.get('type',   '')
    month       = request.args.get('month',  '', type=str)
    year        = request.args.get('year',   '', type=str)
    tag_filter  = request.args.get('tag',    '').strip()

    q = Transaction.query.filter_by(user_id=current_user.id)
    if search:
        q = q.filter(Transaction.description.ilike(f'%{search}%'))
    if type_filter in ('income', 'expense'):
        q = q.filter_by(type=type_filter)
    if month.isdigit():
        q = q.filter(extract('month', Transaction.date) == int(month))
    if year.isdigit():
        q = q.filter(extract('year', Transaction.date) == int(year))
    if tag_filter:
        q = q.filter(Transaction.tag.ilike(f'%{tag_filter}%'))

    paginated = (q.order_by(Transaction.date.desc(), Transaction.created_at.desc())
                  .paginate(page=page, per_page=10, error_out=False))

    all_tags = db.session.query(Transaction.tag)\
        .filter(Transaction.user_id == current_user.id,
                Transaction.tag != None,
                Transaction.tag != '')\
        .distinct().all()
    all_tags = [t[0] for t in all_tags if t[0]]

    return render_template('transaction/transaction_list.html',
        title='Transactions', transactions=paginated,
        search=search, type_filter=type_filter,
        tag_filter=tag_filter, all_tags=all_tags)

@transaction.route('/calendar')
@login_required
def calendar():
    now   = datetime.now()
    month = request.args.get('month', now.month, type=int)
    year  = request.args.get('year',  now.year,  type=int)

    transactions = Transaction.query.filter(
        Transaction.user_id == current_user.id,
        extract('month', Transaction.date) == month,
        extract('year',  Transaction.date) == year,
    ).all()

    events = {}
    for t in transactions:
        key = t.date.strftime('%Y-%m-%d')
        if key not in events:
            events[key] = {'income': 0, 'expense': 0, 'items': []}
        events[key][t.type] += float(t.amount)
        events[key]['items'].append({
            'id':          t.id,
            'type':        t.type,
            'amount':      float(t.amount),
            'description': t.description or '',
            'category':    f"{t.category.icon} {t.category.name}",
            'tag':         t.tag or '',
        })

    current_date = datetime(year, month, 1)
    prev_date    = current_date - relativedelta(months=1)
    next_date    = current_date + relativedelta(months=1)

    return render_template('transaction/transaction_calendar.html',
        title='Calendar',
        events=events,
        events_json=json.dumps(events),
        month=month, year=year,
        month_name=current_date.strftime('%B %Y'),
        prev_month=prev_date.month, prev_year=prev_date.year,
        next_month=next_date.month, next_year=next_date.year,
    )

@transaction.route('/export')
@login_required
def export_csv():
    search      = request.args.get('search', '').strip()
    type_filter = request.args.get('type',   '')
    month       = request.args.get('month',  '', type=str)
    year        = request.args.get('year',   '', type=str)
    tag_filter  = request.args.get('tag',    '').strip()

    q = Transaction.query.filter_by(user_id=current_user.id)
    if search:
        q = q.filter(Transaction.description.ilike(f'%{search}%'))
    if type_filter in ('income', 'expense'):
        q = q.filter_by(type=type_filter)
    if month.isdigit():
        q = q.filter(extract('month', Transaction.date) == int(month))
    if year.isdigit():
        q = q.filter(extract('year', Transaction.date) == int(year))
    if tag_filter:
        q = q.filter(Transaction.tag.ilike(f'%{tag_filter}%'))

    transactions = q.order_by(Transaction.date.desc()).all()

    output = io.StringIO()
    output.write('\ufeff')   # ← BOM บอก Excel ว่าเป็น UTF-8
    writer = csv.writer(output)
    writer.writerow(['Date', 'Type', 'Category', 'Description', 'Tag', 'Amount (THB)'])
    for t in transactions:
        writer.writerow([
            t.date.strftime('%Y-%m-%d %H:%M'),
            t.type.capitalize(),
            f"{t.category.icon} {t.category.name}",
            t.description or '',
            t.tag or '',
            float(t.amount),
        ])

    output.seek(0)
    filename = f"transactions_{datetime.now().strftime('%Y%m%d')}.csv"
    return Response(
        output.getvalue().encode('utf-8-sig'),
        mimetype='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

@transaction.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form    = TransactionForm()
    choices = category_choices()
    form.category_id.choices = [(c[0], c[1]) for c in choices]
    if form.validate_on_submit():
        slip = save_slip(form.slip_image.data) if form.slip_image.data else None
        t = Transaction(
            amount=form.amount.data,           type=form.type.data,
            category_id=form.category_id.data, description=form.description.data,
            tag=form.tag.data or None,
            date=form.date.data,               slip_image=slip,
            user_id=current_user.id,
        )
        db.session.add(t)
        db.session.commit()
        flash('Transaction saved! ✅', 'success')

        # Budget Alert
        if form.type.data == 'expense':
            from app.models.budget import Budget
            now = t.date
            b = Budget.query.filter_by(
                user_id=current_user.id,
                category_id=form.category_id.data,
                month=now.month, year=now.year
            ).first()
            if b:
                spent = float(
                    db.session.query(
                        db.func.coalesce(db.func.sum(Transaction.amount), 0))
                    .filter(
                        Transaction.user_id     == current_user.id,
                        Transaction.category_id == form.category_id.data,
                        Transaction.type        == 'expense',
                        extract('month', Transaction.date) == now.month,
                        extract('year',  Transaction.date) == now.year,
                    ).scalar()
                )
                pct      = int(spent / float(b.amount) * 100) if b.amount else 0
                cat      = next((c for c in choices if c[0] == form.category_id.data), None)
                cat_name = cat[1] if cat else 'Category'
                if pct >= 100:
                    flash(f'⚠️ Budget exceeded for {cat_name}! ({pct}% used)', 'danger')
                elif pct >= 80:
                    flash(f'🔔 Budget warning for {cat_name} — {pct}% used', 'warning')

        return redirect(url_for('transaction.index'))
    return render_template('transaction/transaction_form.html',
        form=form, title='Add Transaction', is_edit=False,
        category_types={ c[0]: c[2] for c in choices })

@transaction.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(id):
    t       = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form    = TransactionForm(obj=t)
    choices = category_choices()
    form.category_id.choices = [(c[0], c[1]) for c in choices]
    if form.validate_on_submit():
        if form.slip_image.data:
            t.slip_image = save_slip(form.slip_image.data)
        t.amount      = form.amount.data
        t.type        = form.type.data
        t.category_id = form.category_id.data
        t.description = form.description.data
        t.tag         = form.tag.data or None
        t.date        = form.date.data
        db.session.commit()
        flash('Transaction updated! ✅', 'success')
        return redirect(url_for('transaction.index'))
    return render_template('transaction/transaction_form.html',
        form=form, title='Edit Transaction', is_edit=True, transaction=t,
        category_types={ c[0]: c[2] for c in choices })

@transaction.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_transaction(id):
    t = Transaction.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(t)
    db.session.commit()
    flash('Transaction deleted.', 'warning')
    return redirect(url_for('transaction.index'))