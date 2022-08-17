from flask import Flask
from flask_caching import Cache
from flask_socketio import SocketIO
from flask_cors import CORS

from .routes import app_routes 
from . import utils
utils.init_logging()

application = Flask(__name__)
CORS(application, resources={r"/*": {"origins": "*"}})
application.debug = True
application.config.from_pyfile('../config.py')
application.config['CORS_HEADERS'] = 'Content-Type'

socketio = SocketIO(application, cors_allowed_origins='*')
cache = Cache(application)

application.register_blueprint(app_routes)

from .tello import tello_routes, tello_automation_routes
application.register_blueprint(tello_routes)
application.register_blueprint(tello_automation_routes)

from .tello import drone

from . import processes

if __name__ == "__main__":
    application.run()