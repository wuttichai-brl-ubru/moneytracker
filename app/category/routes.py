from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.category.forms import CategoryForm
from app.models.category import Category

category = Blueprint('category', __name__, template_folder='templates')

@category.route('/')
@login_required
def index():
    search = request.args.get('search', '').strip()
    q = Category.query.filter_by(user_id=current_user.id)
    if search:
        q = q.filter(Category.name.ilike(f'%{search}%'))
    cats = q.order_by(Category.type, Category.name).all()
    return render_template('category/category_list.html',
        title='Categories', categories=cats, search=search)

@category.route('/add', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        c = Category(name=form.name.data, type=form.type.data,
                     icon=form.icon.data, user_id=current_user.id)
        db.session.add(c)
        db.session.commit()
        flash(f'Category "{c.name}" added! ✅', 'success')
        return redirect(url_for('category.index'))
    return render_template('category/category_form.html',
        form=form, title='Add Category', is_edit=False)

@category.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    c    = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = CategoryForm(obj=c)
    if form.validate_on_submit():
        c.name = form.name.data
        c.type = form.type.data
        c.icon = form.icon.data
        db.session.commit()
        flash('Category updated! ✅', 'success')
        return redirect(url_for('category.index'))
    return render_template('category/category_form.html',
        form=form, title='Edit Category', is_edit=True, category=c)

@category.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    c = Category.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if c.transactions:
        flash("Can't delete — this category has existing transactions.", 'danger')
        return redirect(url_for('category.index'))
    db.session.delete(c)
    db.session.commit()
    flash('Category deleted.', 'warning')
    return redirect(url_for('category.index'))