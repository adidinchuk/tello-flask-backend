from . import cache
from . import drone
from . import socketio
from . import application
import time

import logging

LOGGER = logging.getLogger('app')

VIDEO_TRANSFER_FRAME_RATE = 30
DRONE_STATE_TRANSFER_RATE = 2

from threading import Lock
state_process_thread = None
state_process_thread_lock = Lock()
video_process_thread = None
video_thread_lock = Lock()

@socketio.on('connect')
def start_threads(json):
    """
    Initialize the websocket threads when the first subscriber connects
    """
    LOGGER.info('New device connected to the drone state websocket.')
    global state_process_thread
    global video_process_thread
    if state_process_thread is None:        
        state_process_thread = socketio.start_background_task(drone_state_processing_job, application)
        LOGGER.info('State forwarding thread initialized.')
    if video_process_thread is None:
        video_process_thread = socketio.start_background_task(process_video_stream, application)
        LOGGER.info('Video forwarding thread initialized.')

def drone_state_processing_job(app):
    """
    This function pulls the current frone state from the cache 
    and forwards the data to websocket subscribers 
    """
    while True:
        if drone.get_current_state() != cache.get('drone_state'):
            cache.set('drone_state', drone.get_current_state())
            data = cache.get('drone_state')
            speed = cache.get('speed')
            wifi = cache.get('wifi')
            if(speed != None and wifi != None):
                data["other"] = {"speed": speed["data"], "wifi": wifi["data"]}
            socketio.emit('dronestate', data) 
        socketio.sleep(DRONE_STATE_TRANSFER_RATE)   

import cv2
import base64

def process_video_stream(app):   
    """
    frame processing should happen in this loop, currently the function 
    forwards frames downstream to websocket subscribers
    """ 
    while True:
        try:
            if(len(drone.get_current_state()) != 0):
                img = drone.get_frame_read().frame                 
                cache.set('last_frame', img)    
                frame = cv2.cvtColor(img , cv2.COLOR_BGR2RGB)
                frame = cv2.imencode('.jpg', frame)[1].tobytes()                   
                frame= base64.encodebytes(frame).decode("utf-8")
                forward_frame(frame)
            else:
                socketio.sleep(1)
        except Exception as e: 
            print(e)
        socketio.sleep(1/VIDEO_TRANSFER_FRAME_RATE)

def forward_frame(json):	
	socketio.emit('video', json, engineio_logger=False, logger=False )