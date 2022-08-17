from app import application
from app import socketio
from config import *

if __name__== "__main__":
    socketio.run(application, host=API_IP_ADDRESS, port=API_PORT, use_reloader=False, log_output=False)