from . import db
from flask_login import UserMixin
from datetime import datetime

"""Database model definitions for BookHoard."""

class Book(db.Model):
    """Represents a book entry con metadatos y portada almacenada."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    author = db.Column(db.String(100))
    synopsis = db.Column(db.String(10000))
    cover = db.Column(db.LargeBinary, nullable=True)
    cover_mimetype = db.Column(db.String(50), nullable=True)
    type_book = db.Column(db.String(50))
    category = db.Column(db.String(50))
    isbn = db.Column(db.String(20), unique=True)
    publish_date = db.Column(db.DateTime, nullable=True)
    language = db.Column(db.String(50))
    pages = db.Column(db.Integer)
    review_id = db.relationship('Review')
    shelf_id = db.relationship('Shelf')
    tags_id = db.relationship('Tags')
    statuses = db.relationship('BookStatus', backref='book', lazy=True)

class BookStatus(db.Model):
    """Estado de un libro asociado a un usuario.

    Almacena si el libro es propiedad del usuario y su estado de lectura.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    owned = db.Column(db.String(20), default="not owned")
    reading_status = db.Column(db.String(30), default='not read')
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='user_book_status_uc'),)

class Shelf(db.Model):
    """Registra libros agrupados por una estantería creada por el usuario."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

class Tags(db.Model):
    """Etiqueta asociada a un libro y un usuario."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

class Review(db.Model):
    """Reseña de un libro escrita por un usuario."""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

class User(db.Model,UserMixin):
    """Modelo de usuario que incluye autenticación y relaciones con libros."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    shelf_id = db.relationship('Shelf')
    tags_id = db.relationship('Tags')
    review_id = db.relationship('Review')
    book_statuses = db.relationship('BookStatus', backref='user', lazy=True)