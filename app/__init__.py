from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    app.static_folder = '../static'
    app.template_folder = '../templates'

    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'

    from app.routes.auth import auth_bp
    from app.routes.raffle import raffle_bp
    from app.routes.number import number_bp
    from app.models import User

    app.register_blueprint(auth_bp)
    app.register_blueprint(raffle_bp)
    app.register_blueprint(number_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app