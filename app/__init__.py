from flask import Flask
from .routes import app_routes  
from flask_caching import Cache
from flask_socketio import SocketIO
from flask_cors import CORS

import logging

HANDLER = logging.StreamHandler()
FORMATTER = logging.Formatter('[%(levelname)s] %(filename)s - %(lineno)d - %(message)s')
HANDLER.setFormatter(FORMATTER)
LOGGER = logging.getLogger('app')
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)

application = Flask(__name__)

CORS(application, resources={r"/*": {"origins": "*"}})
application.debug = True
application.config.from_pyfile('../config.py')
application.config['CORS_HEADERS'] = 'Content-Type'

socketio = SocketIO(application, cors_allowed_origins='*')

cache = Cache(application)

from .tello import tello_routes
from .tello import drone

application.register_blueprint(app_routes)
application.register_blueprint(tello_routes)

from . import processes

if __name__ == "__main__":
    application.run()