import os
from flask import Flask
from flask_cors import CORS, cross_origin
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from batch_time import batch_time_bp
from city import city_bp
from state import state_bp
from country import country_bp
from course_content import course_content_bp
from course_mode import course_mode_bp
from model import db
from agent import agent_bp
from trainer import trainer_bp
from branch import branch_bp
from course import course_bp
from lead import lead_bp
from payment_mode import payment_mode_bp
from receipt import receipt_bp
from source import source_bp
from student import student_bp
from user import user_bp
from user_role import user_role_bp
from submitted_leads import submitted_lead_bp
from batch import batch_bp

# SQLALCHEMY_DATABASE_URL = f'mysql://piidm_dev:piidm_dev_password123@localhost:3306/piidm_dev'
# SQLALCHEMY_DATABASE_URL = f'mysql://piidm_online:piidm_online_password123@localhost:3306/piidm_online'
# SQLALCHEMY_DATABASE_URL = f'sqlite:////Users/nitinsolanki/Documents/codemania/piidm-backend/piidm_online_sqlite.db'
SQLALCHEMY_DATABASE_URL = f'sqlite:////root/codemania/piidm-backend/piidm_online_sqlite.db'
# engine = create_engine(SQLALCHEMY_DATABASE_URL, convert_unicode=True, pool_size=1, max_overflow=0,
#                        pool_recycle=1800, pool_pre_ping=True)
engine = create_engine(SQLALCHEMY_DATABASE_URL, convert_unicode=True)
Session = scoped_session(sessionmaker(autocommit=True, bind=engine))


def create_app():
    """
    Flask app configuration and setup
    """
    app = Flask(__name__)
    CORS(app)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret'
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URL
    app.session = Session
    migrate = Migrate()
    db.init_app(app)
    migrate.init_app(app, db)
    return app


app = create_app()
app.register_blueprint(user_role_bp)
app.register_blueprint(user_bp)
app.register_blueprint(branch_bp)
app.register_blueprint(course_bp)
app.register_blueprint(course_mode_bp)
app.register_blueprint(course_content_bp)
app.register_blueprint(source_bp)
app.register_blueprint(agent_bp)
app.register_blueprint(trainer_bp)
app.register_blueprint(country_bp)
app.register_blueprint(state_bp)
app.register_blueprint(city_bp)
app.register_blueprint(batch_time_bp)
app.register_blueprint(lead_bp)
app.register_blueprint(student_bp)
app.register_blueprint(payment_mode_bp)
app.register_blueprint(receipt_bp)
app.register_blueprint(submitted_lead_bp)
app.register_blueprint(batch_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3002)

