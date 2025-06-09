from flask_socketio import join_room, leave_room, emit
from flask_login import current_user
from flask import url_for  # dodaj to!
from app.models import Chat, Message, db

def init_socket_events(socketio):
    @socketio.on("join")
    def handle_join(data):
        room = f"chat_{data['chat_id']}"
        join_room(room)
        print(f"{current_user.username} joined room {room}")

    @socketio.on("send_message")
    def handle_send_message(data):
        chat_id = data['chat_id']
        room = f"chat_{chat_id}"
        chat = Chat.query.get(chat_id)

        if not chat or current_user not in chat.participants:
            print("Unauthorized or invalid chat.")
            return

        msg = Message(content=data["message"], sender=current_user, chat=chat)
        db.session.add(msg)
        db.session.commit()

        # Ustal pełną ścieżkę do zdjęcia profilowego
        if current_user.profile_image:
            profile_image_url = url_for('static', filename='profile_pics/' + current_user.profile_image)
        else:
            profile_image_url = url_for('static', filename='img/default_avatar.png')

        message_data = {
            "username": current_user.username,
            "message": msg.content,
            "timestamp": msg.timestamp.strftime("%H:%M"),
            "profile_image": profile_image_url,  # tutaj poprawione
            "sender_id": current_user.id,
        }

        emit("receive_message", {**message_data, "is_current_user": True})
        emit("receive_message", {**message_data, "is_current_user": False}, to=room, include_self=False)

