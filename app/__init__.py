from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_socketio import SocketIO

load_dotenv()

socketio = SocketIO()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Rejestracja blueprintów
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.posts import posts_bp
    from app.users import users_bp
    from app.admin.routes import admin_bp
    from app.admin_user_init import create_admin
    from app.chat.routes import chat_bp
    from app.chat.socket_events import init_socket_events
    from app.models import Comment


    init_socket_events(socketio)
    create_admin(app)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(users_bp, url_prefix='/user')
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)


    return app

