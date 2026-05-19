"""Website package initialization for BookHoard.

This module creates the Flask application, configures SQLAlchemy and
Flask-Login, registers blueprints, and initializes the local SQLite
database when needed.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'views.login'  # type: ignore
DB_NAME = "bookhoard_database.db"


def create_app():
    """Create and configure the Flask app for BookHoard."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'bookshoarder'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    login_manager.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Book

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    create_database(app)

    return app

def create_database(app):
    """Create the SQLite database file if it does not already exist."""
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')
