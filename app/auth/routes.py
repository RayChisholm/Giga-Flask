from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse
from app import db
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

        if not user.active:
            flash('Your account has been deactivated. Please contact an administrator.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)

        # Redirect to next page or home
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')

        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)


@auth_bp.route('/logout')
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role='user'  # Default role
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you are now registered! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)
