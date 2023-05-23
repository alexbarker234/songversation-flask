import glob
import os
import logging
from pathlib import Path
from flask_socketio import SocketIO
from config import Config
from logging.handlers import RotatingFileHandler
from datetime import date

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_assets import Environment, Bundle

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
assets = Environment(app)

socketio = SocketIO(app)

import os

# bundles - dynamically load all files in css & js files

css_files = [str(path.relative_to('app/static')) for path in Path('app/static/css').rglob('*.css')]
css = Bundle(*css_files, output='gen/packed.css')
assets.register('css_all', css)

# could potentially include jQuery & bootstrap.js in here
js_files = [str(path.relative_to('app/static')) for path in Path('app/static/js').rglob('*.js')]
css = Bundle(*js_files, output='gen/packed.js')
assets.register('js_all', css)

print("Starting Songversation...")

from app import routes, models, errors, api, auth, cache_manager, exceptions, sockets


if __name__ == "__main__":
    socketio.run(app, log_output=False)