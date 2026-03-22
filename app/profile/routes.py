from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.profile.forms import UpdateProfileForm
from PIL import Image
from werkzeug.datastructures import FileStorage
import os, secrets

profile = Blueprint('profile', __name__, template_folder='templates')

def save_profile_pic(file):
    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{secrets.token_hex(8)}.{ext}"
    path     = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    img      = Image.open(file)
    img.thumbnail((200, 200))
    img.save(path)
    return filename

@profile.route('/')
@login_required
def view_profile():
    return render_template('profile/profile_detail.html', title='My Profile')

@profile.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm(obj=current_user)
    if form.validate_on_submit():
        # ✅ เช็คว่าเป็น file จริงๆ ไม่ใช่ string
        if isinstance(form.profile_image.data, FileStorage) and form.profile_image.data.filename:
            current_user.profile_image = save_profile_pic(form.profile_image.data)
        current_user.fullname = form.fullname.data or None
        current_user.username = form.username.data
        current_user.email    = form.email.data
        db.session.commit()
        flash('Profile updated! ✅', 'success')
        return redirect(url_for('profile.view_profile'))
    return render_template('profile/profile_form.html',
        form=form, title='Edit Profile')