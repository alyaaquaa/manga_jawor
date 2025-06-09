from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Chat, Message, db

chat_bp = Blueprint('chat', __name__, template_folder='templates')

@chat_bp.route('/chat', methods=['GET'])
@login_required
def index():
    search_query = request.args.get('q', '').strip()
    users = []
    search_error = None

    if search_query:
        if search_query.lower() == current_user.username.lower():
            search_error = "Nie możesz wyszukiwać samego siebie."
        else:
            users = User.query.filter(
                User.username.ilike(f"%{search_query}%"),
                User.id != current_user.id
            ).all()
            if not users:
                search_error = f"Użytkownik o nazwie '{search_query}' nie istnieje."

    user_chats = current_user.chats
    # Mapuj czaty 1:1 z użytkownikiem
    existing_chats = {
        participant.id: chat for chat in current_user.chats if not chat.is_group
        for participant in chat.participants if participant != current_user
    }
    return render_template(
        'chat/chat.html',
        users=users,
        chats=user_chats,
        search_error=search_error,
        existing_chats=existing_chats,
        chat_page=True
    )


@chat_bp.route('/chat/start/<int:user_id>')
@login_required
def start_chat(user_id):
    if user_id == current_user.id:
        flash("Nie możesz rozpocząć czatu z samym sobą.", "warning")
        return redirect(url_for('chat.index'))

    other_user = User.query.get_or_404(user_id)

    # Sprawdź, czy czat już istnieje
    existing_chat = Chat.query.filter(
        Chat.participants.contains(current_user),
        Chat.participants.contains(other_user),
        Chat.is_group == False
    ).first()

    if existing_chat:
        flash(f"Czat z użytkownikiem {other_user.username} już istnieje.", "info")
        return redirect(url_for('chat.view_chat', chat_id=existing_chat.id))

    # Tworzenie nowego czatu
    new_chat = Chat(is_group=False)
    new_chat.participants.append(current_user)
    new_chat.participants.append(other_user)
    db.session.add(new_chat)
    db.session.commit()
    return redirect(url_for('chat.view_chat', chat_id=new_chat.id))


@chat_bp.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
@login_required
def view_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if current_user not in chat.participants:
        return redirect(url_for('chat.index'))

    # Sprawdź, czy któryś z uczestników zablokował drugiego (tylko dla czatów 1:1)
    other_user = next((user for user in chat.participants if user != current_user), None)
    is_blocked = False
    if other_user:
        is_blocked = other_user in current_user.blocked_users or current_user in other_user.blocked_users

    if request.method == 'POST':
        if is_blocked:
            flash("Nie możesz wysłać wiadomości, ponieważ jeden z użytkowników zablokował rozmówcę.", "danger")
            return redirect(url_for('chat.view_chat', chat_id=chat.id))

        message_text = request.form.get('message')
        if message_text:
            message = Message(content=message_text, sender=current_user, chat=chat)
            db.session.add(message)
            db.session.commit()

    messages = chat.messages
    return render_template('chat/chat_box.html', chat=chat, messages=messages, chat_id=chat.id, is_blocked=is_blocked, chat_page=True,   user=other_user)

@chat_bp.route('/chat/block/<int:user_id>', methods=['POST'])
@login_required
def block_user(user_id):
    user_to_block = User.query.get_or_404(user_id)
    if user_to_block == current_user:
        flash("Nie możesz zablokować samego siebie.", "warning")
    elif user_to_block in current_user.blocked_users:
        flash(f"Użytkownik {user_to_block.username} już jest zablokowany.", "info")
    else:
        current_user.blocked_users.append(user_to_block)
        db.session.commit()
        flash(f"Zablokowano użytkownika {user_to_block.username}.", "success")
    return redirect(url_for('chat.index'))


@chat_bp.route('/chat/unblock/<int:user_id>', methods=['POST'])
@login_required
def unblock_user(user_id):
    user_to_unblock = User.query.get_or_404(user_id)
    if user_to_unblock in current_user.blocked_users:
        current_user.blocked_users.remove(user_to_unblock)
        db.session.commit()
        flash(f"Odbokowano użytkownika {user_to_unblock.username}.", "success")
    else:
        flash("Ten użytkownik nie jest zablokowany.", "info")
    return redirect(url_for('chat.index'))


@chat_bp.route('/chat/delete/<int:chat_id>', methods=['POST'])
@login_required
def delete_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if current_user in chat.participants:
        db.session.delete(chat)
        db.session.commit()
        flash("Czat został usunięty.", "success")
    else:
        flash("Nie masz uprawnień do usunięcia tego czatu.", "danger")
    return redirect(url_for('chat.index'))

