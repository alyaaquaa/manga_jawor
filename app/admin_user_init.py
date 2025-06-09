from app import db
from app.models import User
from werkzeug.security import generate_password_hash

def create_admin(app):
    with app.app_context():  # <- KONIECZNE!
        admin_username = app.config['ADMIN_USERNAME']
        admin_email = app.config['ADMIN_EMAIL']
        admin_password = app.config['ADMIN_PASSWORD']

        existing_admin = User.query.filter_by(username=admin_username).first()
        if not existing_admin:
            admin_user = User(
                username=admin_username,
                email=admin_email,
                password=generate_password_hash(admin_password),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print(f'✅ Admin "{admin_username}" utworzony.')
        else:
            print(f'ℹ️ Admin "{admin_username}" już istnieje.')

