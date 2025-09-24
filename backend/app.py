from flask import Flask
from application.config import LocalDevelopmentConfig
from application.database import db
from application.model import User
from application.security import jwt

app = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)

    db.init_app(app)
    jwt.init_app(app)
    return app 

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(email='admin@parking.com').first()
        if not admin:
            admin = User(
                full_name='Admin User',
                username='admin',
                email='admin@parking.com',
                phone='9999999999',
                address='Admin Office',
                pin_code='000000',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created!")
            # vinshi
    app.run(debug=True)


