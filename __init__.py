from flask import Flask
from .auth import auth_bp
from .config import Config

def create_app():
  "Create app and register blueprints"
  app = Flask(__name__)
  app.register_blueprint(auth_bp)
  app.config.from_object(Config)

  return app