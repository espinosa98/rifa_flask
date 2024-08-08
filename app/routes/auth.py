#  Flask
from flask import Blueprint, render_template, redirect, url_for, flash
from app import db, bcrypt
from flask_login import login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError

# propios
from app.forms import RegisterForm, LoginForm
from app.models import User
from config import Config


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        register_key = form.register_key.data
        if register_key != Config.REGISTER_KEY:
            flash('Clave de registro incorrecta.', 'danger')
            return redirect(url_for('auth.register'))
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Cuenta creada exitosamente!', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            flash('El correo electrónico o el nombre de usuario ya están registrados. Por favor, intenta con otros.',
                  'danger')
            return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Inicio de sesión exitoso!', 'success')
            return redirect(url_for('raffle.admin'))
        else:
            flash('Inicio de sesión fallido. Por favor verifica tu email y contraseña.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('raffle.index'))