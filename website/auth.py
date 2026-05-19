from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User

auth = Blueprint('auth', __name__)

"""Módulo de autenticación para registro de usuarios y manejo de sesión."""


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration and login after a successful signup.

    Validates form fields, hashes the password, creates the user record,
    and logs in the new user automatically.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='Registererror')
        elif len(email) < 4: #type: ignore
            flash('Email must be greater than 3 characters.', category='Registererror')
        elif len(name) < 2: #type: ignore
            flash('Name must be greater than 1 character.', category='Registererror')
        elif password != confirmPassword:
            flash('Passwords don\'t match.', category='Registererror')
        elif len(password) < 7: #type: ignore
            flash('Password must be at least 7 characters.', category='Registererror')
        else:
            new_user = User(email=email, name=name, password=generate_password_hash(password, method='scrypt')) # type: ignore
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            flash('Account created!', category='Registersuccess')
            return redirect(url_for('views.home'))

    return render_template('register.html')

