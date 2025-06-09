# app/auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app.auth import auth_bp
from app.models import User
from app.auth.forms import RegisterForm, LoginForm
from app import db

@auth_bp.route('/register', methods=['GET', 'POST'])

def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username = form.username.data,
            email = form.email.data,
            password = hashed_password
        )
        db.session.add(new_user)
        db.session.commit()  # Zatwierdzenie transakcji
        flash('Rejestracja zakończona sukcesem! Zaloguj się.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Nieprawidłowy email lub hasło', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Wylogowano.', 'info')
    return redirect(url_for('main.index'))

