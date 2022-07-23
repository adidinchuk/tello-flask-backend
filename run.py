from app import application
from app import socketio

if __name__== "__main__":
    socketio.run(application, host='192.168.0.14', port=5000, use_reloader=False, log_output=False)