from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from . import posts_bp
from .forms import PostForm
from werkzeug.utils import secure_filename
import os
from flask import current_app
from app.models import Tag
from sqlalchemy import or_


UPLOAD_FOLDER = 'app/static/uploads'  # Folder na zdjęcia
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@posts_bp.route('/')
def index():
    sort_order = request.args.get('sort', 'desc')
    selected_genre = request.args.get('genre')
    selected_tag = request.args.get('tag')
    search_query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Post.query

    # Filtrowanie po gatunku
    if selected_genre:
        query = query.filter(Post.genres.like(f'%{selected_genre}%'))

    # Filtrowanie po tagu
    if selected_tag:
        query = query.join(Post.tags).filter(Tag.name == selected_tag)

        # 🔍 Filtrowanie po tytule (wyszukiwanie)
    if search_query:
        query = query.filter(or_(
            Post.title.ilike(f'%{search_query}%'),
            Post.content.ilike(f'%{search_query}%')
        ))

    # Sortowanie
    if sort_order == 'asc':
        query = query.order_by(Post.created_at.asc())
    elif sort_order == 'title_asc':
        query = query.order_by(Post.title.asc())
    elif sort_order == 'title_desc':
        query = query.order_by(Post.title.desc())
    else:
        query = query.order_by(Post.created_at.desc())

    posts = query.paginate(page=page, per_page=5)

    # Lista unikalnych gatunków i tagów do formularza
    all_genres = sorted(set(g for p in Post.query.all() for g in (p.genres or '').split(',') if g))
    all_tags = Tag.query.order_by(Tag.name).all()

    return render_template('posts/posts.html', posts=posts, sort_order=sort_order, selected_genre=selected_genre, selected_tag=selected_tag,
    all_genres=all_genres, all_tags=all_tags, search_query=search_query,)


@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()

    if form.validate_on_submit():
        # Obsługa obrazu przed stworzeniem obiektu
        filename = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            upload_path = os.path.join(current_app.static_folder, 'uploads', filename)
            form.image.data.save(upload_path)

        genres_list = form.genres.data or []
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user,
            genres=','.join(genres_list),
            image_url=form.image_url.data,
            image_filename=filename  # teraz już poprawna wartość!
        )

        # Obsługa tagów
        tag_names = [name.strip() for name in (form.tags.data or '').split(',') if name.strip()]
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
                db.session.add(tag)
            post.tags.append(tag)

        db.session.add(post)
        db.session.commit()
        flash('Post utworzony!', 'success')
        return redirect(url_for('posts.index'))

    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{error}", "danger")

    return render_template('posts/create.html', form=form, image_url=None)


from app.models import Post
from app.posts.forms import CommentForm
from app.models import Comment

@posts_bp.route('/<int:post_id>', methods=['GET', 'POST'])
def show(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)

    # Pobieramy wszystkie komentarze do posta, najnowsze jako pierwsze
    comments = Comment.query.filter_by(post_id=post.id) \
        .order_by(Comment.created_at.desc()) \
        .paginate(page=page, per_page=5)

    form = CommentForm()
    return render_template('posts/show.html', post=post, comments=comments, form=form, image_url=None)

@posts_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user and not current_user.is_admin:
        abort(403)

    form = PostForm(obj=post)

    # Przy GET przypisz gatunki jako listę do pola formularza
    if request.method == 'GET':
        form.genres.data = post.genres.split(',') if post.genres else []
        form.tags.data = ', '.join(tag.name for tag in post.tags)

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.genres = ','.join(form.genres.data or [])
        post.image_url = form.image_url.data

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            upload_path = os.path.join(current_app.static_folder, 'uploads', filename)
            form.image.data.save(upload_path)
            post.image_filename = filename

        # Obsługa tagów przy edycji
        tag_names = [name.strip() for name in (form.tags.data or '').split(',') if name.strip()]
        tags = []
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
                db.session.add(tag)
            tags.append(tag)
        post.tags = tags

        db.session.commit()
        flash('Post zaktualizowany.', 'info')
        return redirect(url_for('posts.show', post_id=post.id))  # lepiej przenieść do podglądu posta

    return render_template('posts/edit.html', form=form, post=post, image_url=None)


@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and not current_user.is_admin:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post usunięty.', 'danger')
    return redirect(url_for('posts.index'))

@posts_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():

        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post_id=post_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Dodano komentarz.', 'success')
    else:
        flash('Nie udało się dodać komentarza.', 'danger')
    return redirect(url_for('posts.show', post_id=post_id))

