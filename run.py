# run.py
from app import create_app, db, socketio
from dotenv import load_dotenv
load_dotenv()

app = create_app()

# Tworzenie tabel w bazie danych
with app.app_context():
    db.create_all()  # Tworzy tabele na podstawie modeli

if __name__ == '__main__':
    socketio.run(app, debug=True)

