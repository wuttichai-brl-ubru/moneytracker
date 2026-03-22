from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.auth.forms import RegistrationForm, LoginForm
from app.models.user import User
from app.models.category import Category

auth = Blueprint('auth', __name__, template_folder='templates')

DEFAULT_CATEGORIES = [
    # ── Income ───────────────────────────────────────────────────
    ('Salary',          'income',  '💼'),
    ('Freelance',       'income',  '💻'),
    ('Business',        'income',  '🏢'),
    ('Investment',      'income',  '📈'),
    ('Bonus',           'income',  '🎁'),
    ('Gift',            'income',  '🎀'),
    ('Other Income',    'income',  '💰'),

    # ── Food & Drink ─────────────────────────────────────────────
    ('Food',            'expense', '🍜'),
    ('Coffee & Drinks', 'expense', '☕'),
    ('Groceries',       'expense', '🛍️'),

    # ── Transport ────────────────────────────────────────────────
    ('Transport',       'expense', '🚌'),
    ('Fuel',            'expense', '⛽'),
    ('Car Maintenance', 'expense', '🔧'),

    # ── Housing ──────────────────────────────────────────────────
    ('Rent',            'expense', '🏠'),
    ('Utilities',       'expense', '💡'),
    ('Internet',        'expense', '📶'),
    ('Phone Bill',      'expense', '📱'),

    # ── Health ───────────────────────────────────────────────────
    ('Health',          'expense', '💊'),
    ('Fitness',         'expense', '🏋️'),

    # ── Shopping ─────────────────────────────────────────────────
    ('Shopping',        'expense', '🛒'),
    ('Clothing',        'expense', '👕'),
    ('Electronics',     'expense', '📱'),

    # ── Entertainment ────────────────────────────────────────────
    ('Entertainment',   'expense', '🎮'),
    ('Travel',          'expense', '✈️'),
    ('Dining Out',      'expense', '🍽️'),

    # ── Education ────────────────────────────────────────────────
    ('Education',       'expense', '📚'),
    ('Books',           'expense', '📖'),

    # ── Other ────────────────────────────────────────────────────
    ('Insurance',       'expense', '🛡️'),
    ('Savings',         'expense', '🐷'),
    ('Donation',        'expense', '🤝'),
    ('Other',           'expense', '📦'),
]

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    fullname=form.fullname.data or None)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        for name, type_, icon in DEFAULT_CATEGORIES:
            db.session.add(Category(name=name, type=type_, icon=icon, user_id=user.id))
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, title='Register')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        identity = form.identity.data.strip()
        user = User.query.filter(
            (User.email == identity) | (User.username == identity)
        ).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.display_name}! 👋', 'success')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('auth/login.html', form=form, title='Log In')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))