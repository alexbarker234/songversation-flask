import os
import logging
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

# bundles
css = Bundle('css/main.css', 'css/nav.css', 'css/animation.css', output='gen/packed.css')
assets.register('css_all', css)

# logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/flasktest_{}.log'.format(date.today()))
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('flasktest startup')

from app import routes, models, errors