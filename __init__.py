from flask import Flask, g
from .auth import auth_bp
from .admin import admin_bp
from .teachr import teachr_bp
from .config import Config
from .models import db, SchoolInfo, Teacher, User, Grade
from flask_migrate import Migrate
from flask_login import LoginManager

 

def create_app():
  "Create app and register blueprints"
  app = Flask(__name__)
  migrate = Migrate(app)
  app.register_blueprint(auth_bp)
  app.register_blueprint(admin_bp)
  app.register_blueprint(teachr_bp)
  app.config.from_object(Config)




  # Initialize the SQLAlchemy db instance with the app
  db.init_app(app)

  # Create instance of Migrate
  migrate = Migrate(app, db)
  login_manager = LoginManager(app)

  # Configure the login view
  login_manager.login_view = 'auth.login'  
  login_manager.login_message = "You must be logged in to access this page."
  login_manager.login_message_category = "danger"

  @login_manager.user_loader
  def load_user(user_id):
    return User.query.get(int(user_id))

  # Add the 'before_request' hook
  @app.before_request
  def load_general_info(): 
    try:
      school_info = SchoolInfo.query.all()
      # handle too long school name.
      name = school_info[-1].name
      if len(name) > 1:
        name = (name[:80] + '...') if len(name) > 80 else name
    except IndexError:
      name = 'No School name set yet'  
  
    if school_info: 
        g.general_info = {
            'school_name': name,
            'total_teachers': 12
        }
    else:
      g.general_info = {}

  # Create all database tables if they do not already exist
  with app.app_context():
    db.create_all()
    # Add grades to the database
    grades = [Grade(grade_name=f'Grade {i}') for i in range(1, 10)]
    try:
      db.session.add_all(grades)
      db.session.commit()
    except:
      pass

  return app
