from flask import Flask, render_template
from app.extensions import db, bcrypt, login_manager, migrate
from app.models.user        import User
from app.models.category    import Category
from app.models.transaction import Transaction
from app.models.budget      import Budget
from app.models.goal        import Goal
from flask_wtf.csrf import CSRFProtect

import os
from app.auth.routes        import auth
from app.main.routes        import main
from app.transaction.routes import transaction
from app.category.routes    import category
from app.budget.routes      import budget
from app.profile.routes     import profile
from app.goal.routes        import goal

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI']        = os.environ.get('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH']             = 2 * 1024 * 1024
    app.config['UPLOAD_FOLDER'] = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'static', 'img'
    )
    app.secret_key = os.environ.get('SECRET_KEY')

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.login_view             = 'auth.login'
    login_manager.login_message          = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'



    app.register_blueprint(auth,        url_prefix='/auth')
    app.register_blueprint(main,        url_prefix='/')
    app.register_blueprint(transaction, url_prefix='/transaction')
    app.register_blueprint(category,    url_prefix='/category')
    app.register_blueprint(budget,      url_prefix='/budget')
    app.register_blueprint(profile,     url_prefix='/profile')
    app.register_blueprint(goal,        url_prefix='/goal')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html', title='Page Not Found'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html', title='Server Error'), 500

    return app