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
from country import country_bp
from model import db
from agent import agent_bp
from branch import branch_bp
from course import course_bp
from lead import lead_bp
from receipt import receipt_bp
from source import source_bp
from student import student_bp


# SQLALCHEMY_DATABASE_URL = f'sqlite:///{os.getcwd()}piidm_dev.db'
SQLALCHEMY_DATABASE_URL = f'mysql://piidm_dev:piidm_dev_password123@localhost:3306/piidm_dev'
engine = create_engine(SQLALCHEMY_DATABASE_URL, convert_unicode=True)
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def create_app():
    """
    Flask app configuration and setup
    """
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URL
    app.session = Session
    migrate = Migrate()
    db.init_app(app)
    migrate.init_app(app, db)
    return app


app = create_app()
app.register_blueprint(branch_bp)
app.register_blueprint(course_bp)
app.register_blueprint(source_bp)
app.register_blueprint(agent_bp)
app.register_blueprint(country_bp)
app.register_blueprint(city_bp)
app.register_blueprint(batch_time_bp)
app.register_blueprint(lead_bp)
app.register_blueprint(student_bp)
app.register_blueprint(receipt_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3002)

