"""Main website views and route handlers for BookHoard."""

from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import current_user, login_user, login_required
from werkzeug.security import check_password_hash
from datetime import datetime
import base64
from . import db
from .models import User, Book, BookStatus, Shelf, Tags, Review

views = Blueprint('views',__name__)


@views.route('/', methods=['GET', 'POST']) 
def login():
    """Renderiza la página de login y autentica al usuario.

    Recibe email y contraseña, valida el usuario y crea la sesión.
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
           if check_password_hash(user.password, password): #type: ignore
                login_user(user)
                flash("Login successful!", category='success')
                return redirect(url_for('views.home'))
           else:
                flash("Incorrect password, try again.", category='error')
        else:
            flash("Email does not exist.", category='error')

    return render_template('login.html', boolean=True)

@views.route('/home')
def home():
    """Renderiza la página principal con una selección de libros."""
    books = Book.query.limit(6).all()
    books_for_template = []
    for b in books:
        cover_src = None
        if b.cover:
            mime = getattr(b, 'cover_mimetype', None) or 'image/png'
            cover_b64 = base64.b64encode(b.cover).decode('ascii')
            cover_src = f"data:{mime};base64,{cover_b64}"
        books_for_template.append({
            'id': b.id,
            'title': b.title,
            'author': b.author,
            'cover_src': cover_src,
        })

    return render_template('home.html', books=books_for_template)

@views.route('/book/<int:id>', methods=['GET', 'POST'])
def book(id): 
    """Renderiza detalles del libro y guarda el estado de lectura del usuario."""
    book = Book.query.get_or_404(id)
    status = None
    if current_user.is_authenticated:
        status = BookStatus.query.filter_by(user_id=current_user.id, book_id=id).first()
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('views.login'))
        if not status:
            status = BookStatus()
            status.user_id = current_user.id
            status.book_id = id
            db.session.add(status)
        # owned comes as 'true' or 'false' from the form
        owned = request.form.get('owned')
        status.owned = (owned == 'true')

        reading_status = request.form.get('reading_status')
        if reading_status in ('not read', 'reading', 'finished'):
            status.reading_status = reading_status
        db.session.commit()
        flash('Estado del libro actualizado.', category='Statussuccess')
        return redirect(url_for('views.book', id=id))

    if not status and current_user.is_authenticated:
        status = BookStatus()
        status.user_id = current_user.id
        status.book_id = id

    cover_src = None
    if book.cover:
        mime = getattr(book, 'cover_mimetype', None) or 'image/png'
        cover_b64 = base64.b64encode(book.cover).decode('ascii')
        cover_src = f"data:{mime};base64,{cover_b64}"
    return render_template('book.html', book=book, cover_src=cover_src, status=status)

@views.route('/shelf')
@login_required
def shelf():
    """Muestra los libros del usuario divididos en owned y read, y las estanterías creadas."""
    # get all statuses for current user
    statuses = BookStatus.query.filter_by(user_id=current_user.id).all()

    owned_books = []
    read_books = []

    for s in statuses:
        b = s.book
        if not b:
            continue
        cover_src = None
        if b.cover:
            mime = getattr(b, 'cover_mimetype', None) or 'image/png'
            cover_b64 = base64.b64encode(b.cover).decode('ascii')
            cover_src = f"data:{mime};base64,{cover_b64}"
        book_item = {
            'id': b.id,
            'title': b.title,
            'cover_src': cover_src,
        }

        # put 'reading' with owned
        if s.owned or s.reading_status == 'reading':
            owned_books.append(book_item)
        if s.reading_status == 'finished':
            read_books.append(book_item)

    shelves = {}
    shelf_entries = Shelf.query.filter_by(user_id=current_user.id).all()
    for entry in shelf_entries:
        b = Book.query.get(entry.book_id)
        if not b:
            continue
        cover_src = None
        if b.cover:
            mime = getattr(b, 'cover_mimetype', None) or 'image/png'
            cover_b64 = base64.b64encode(b.cover).decode('ascii')
            cover_src = f"data:{mime};base64,{cover_b64}"
        book_item = {
            'id': b.id,
            'title': b.title,
            'cover_src': cover_src,
        }
        shelves.setdefault(entry.name or 'Untitled', []).append(book_item)

    shelf_list = [{'name': name, 'books': books, 'count': len(books)} for name, books in shelves.items()]

    return render_template('shelf.html', owned_books=owned_books, read_books=read_books, shelf_list=shelf_list)

@views.route('/shelf/delete', methods=['POST'])
@login_required
def delete_shelf():
    """Elimina todas las entradas de una estantería del usuario por nombre."""
    shelf_name = request.form.get('shelf_name')
    if shelf_name:
        Shelf.query.filter_by(user_id=current_user.id, name=shelf_name).delete()
        db.session.commit()
        flash(f"Estantería '{shelf_name}' eliminada.", category='Shelfsuccess')
    else:
        flash('Nombre de estantería inválido.', category='Shelferror')
    return redirect(url_for('views.shelf'))

@views.route('/createshelf', methods=['GET', 'POST'])
@login_required
def createshelf():
    """Renderiza el formulario de creación de estantería y guarda la nueva estantería del usuario."""
    statuses = BookStatus.query.filter_by(user_id=current_user.id).all()
    eligible_books = []
    for s in statuses:
        if s.owned == 'true' or s.reading_status in ('reading', 'finished'):
            b = s.book
            if not b:
                continue
            cover_src = None
            if b.cover:
                mime = getattr(b, 'cover_mimetype', None) or 'image/png'
                cover_b64 = base64.b64encode(b.cover).decode('ascii')
                cover_src = f"data:{mime};base64,{cover_b64}"
            eligible_books.append({
                'id': b.id,
                'title': b.title,
                'cover_src': cover_src,
                'status': s.reading_status,
                'owned': s.owned,
            })

    if request.method == 'POST':
        shelf_title = request.form.get('shelf_title', '').strip()
        selected_ids = request.form.getlist('book_id')
        if not shelf_title:
            flash('Por favor ingresa un título para la estantería.', category='Selecterror')
        elif not selected_ids:
            flash('Selecciona al menos un libro.', category='Selecterror')
        else:
            for book_id in selected_ids:
                try:
                    book_id_int = int(book_id)
                except (ValueError, TypeError):
                    continue
                existing = Shelf.query.filter_by(user_id=current_user.id, book_id=book_id_int, name=shelf_title).first()
                if not existing:
                    new_shelf = Shelf(name=shelf_title, user_id=current_user.id, book_id=book_id_int)#type: ignore
                    db.session.add(new_shelf)
            db.session.commit()
            flash('Estantería creada correctamente.', category='Selectsuccess')
            return redirect(url_for('views.shelf'))

    return render_template('createshelf.html', books=eligible_books)

@views.route('/bestsellers')
def bestsellers():
    """Renderiza la página de bestsellers."""
    return render_template('bestsellers.html')

@views.route('/author')
def author():
    """Renderiza la página de autor."""
    return render_template('author.html')

@views.route('/categories')
def categories():
    """Renderiza la página de categorías."""
    return render_template('categories.html')

@views.route('/registerbook', methods=['GET', 'POST'])
def registerbook():
    """Permite registrar un nuevo libro en la base de datos mediante un formulario."""
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        synopsis = request.form.get('synopsis')
        type_book = request.form.get('book_type')
        category = request.form.get('genre')
        isbn = request.form.get('isbn')
        publish_date_str = request.form.get('publish_date')
        pages = request.form.get('pages')
        cover_file = request.files.get('cover')
        cover = None
        cover_mimetype = None
        if cover_file and getattr(cover_file, 'filename', None):
            cover = cover_file.read()
            cover_mimetype = cover_file.mimetype
        language = request.form.get('language')
        
        book = Book.query.filter_by(isbn=isbn).first()

        if book:
            flash('Book with this ISBN already exists.', category='RegisterBookerror')
            return render_template('registerbook.html')

        if not (title and author and synopsis and type_book and category and isbn and publish_date_str and language and pages):
            flash('All fields with the * are required', category='Registererror')
            return render_template('registerbook.html')

        try:
            publish_date = datetime.strptime(publish_date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            flash('Publication date must be a valid date.', category='Registererror')
            return render_template('registerbook.html')

        try:
            pages_value = int(pages)
        except (ValueError, TypeError):
            flash('Pages must be a valid number.', category='Registererror')
            return render_template('registerbook.html')

        new_book = Book( title=title, author=author, synopsis=synopsis, type_book=type_book, category=category, isbn=isbn, publish_date=publish_date, language=language, pages=pages_value, cover=cover, cover_mimetype=cover_mimetype,) # type: ignore
        db.session.add(new_book)
        db.session.commit()

        flash("Book registered successfully!", category='Booksuccess')
        return redirect(url_for('views.home'))
    return render_template('registerbook.html')