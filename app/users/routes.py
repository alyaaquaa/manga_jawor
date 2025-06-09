from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import Post
from . import users_bp
from .forms import UpdateProfileForm
@users_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UpdateProfileForm(obj=current_user)
    user_posts = Post.query.filter_by(author=current_user).all()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        file = form.profile_image.data
        if file and hasattr(file, 'filename') and file.filename:
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.static_folder, 'profile_pics', filename)
            file.save(upload_path)
            current_user.profile_image = filename

        db.session.commit()
        flash('Profil zaktualizowany!', 'success')
        return redirect(url_for('users.dashboard'))

    return render_template('users/dashboard.html', user=current_user, posts=user_posts, form=form)


