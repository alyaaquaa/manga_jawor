from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Chat, db
from app.decorators import admin_required

admin_bp = Blueprint('admin_bp', __name__, template_folder='templates')

@admin_bp.route('/admin/chats')
@login_required
@admin_required
def chat_list():
    chats = Chat.query.all()
    return render_template('admin/chat_list.html', chats=chats)

@admin_bp.route('/admin/chats/delete/<int:chat_id>', methods=['POST'])
@login_required
@admin_required
def delete_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    db.session.delete(chat)
    db.session.commit()
    flash('Czat został usunięty.', 'success')
    return redirect(url_for('admin_bp.chat_list'))

@admin_bp.route('/admin/users')
@login_required
@admin_required
def user_list():
    users = User.query.all()
    return render_template('admin/user_list.html', users=users)

@admin_bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Nie możesz usunąć samego siebie.', 'danger')
        return redirect(url_for('admin_bp.user_list'))
    db.session.delete(user)
    db.session.commit()
    flash('Użytkownik został usunięty.', 'success')
    return redirect(url_for('admin_bp.user_list'))

@admin_bp.route('/admin/users/edit/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    user.username = request.form.get('username')
    user.email = request.form.get('email')
    db.session.commit()
    flash('Użytkownik zaktualizowany.', 'success')
    return redirect(url_for('admin_bp.user_list'))

