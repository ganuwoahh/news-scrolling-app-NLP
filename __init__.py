from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = 'nlp.db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Jumbassi3'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Jumbassi3@localhost/nlp'
    db.init_app(app)
    
    from .views import views
    from .auth import auth
    
    from .models import User
    
    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')
    
    with app.app_context():    
        create_database(app)
        
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context(): 
            db.create_all()
            print('Created database!')