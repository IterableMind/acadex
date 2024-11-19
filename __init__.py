from flask import Flask
from .auth import auth_bp

def create_app():
  "Create app and register blueprints"
  app = Flask(__name__)
  app.register_blueprint(auth_bp)

  return app