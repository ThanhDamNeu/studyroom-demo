import os
from datetime import datetime

from flask import Flask

from . import db
from .routes import bp


def create_app(config=None):
    app = Flask(__name__, template_folder="../templates")
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-not-secret"),
        DATABASE=os.environ.get("DATABASE_PATH", "studyroom.db"),
        CLOCK=datetime.now,  # tests replace it with a fixed time
    )
    if config:
        app.config.update(config)

    db.init_app(app)
    app.register_blueprint(bp)
    return app
