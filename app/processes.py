from . import cache
from . import drone
from . import socketio
from . import application

import time
import logging
import copy

LOGGER = logging.getLogger('app')

VIDEO_TRANSFER_FRAME_RATE = 30
DRONE_STATE_TRANSFER_RATE = 1
state_forwarding_task = None
video_processing_task = None

def start_task_if_inactive(background_task_object, target_function):
    """
    Launch a socketio background task as provided by the target_function if 
    one is not already assigned to the provided background_task_object
    """
    if background_task_object is None:        
        background_task_object = socketio.start_background_task(target_function, application)
    return background_task_object

@socketio.on('connect')
def start_threads(json):
    """
    Initializing the WebSocket threads when the first subscriber connects
    """
    LOGGER.info('New device connected to the drone state websocket.')
    global state_forwarding_task, video_processing_task
    # Initialize the state forwarding and video processing tasks if not already done
    state_forwarding_task = start_task_if_inactive(state_forwarding_task, process_drone_state)
    video_processing_task = start_task_if_inactive(video_processing_task, process_video_frame)

def process_drone_state(app):
    """
    This function pulls the current frone state from the cache 
    and forwards the data to websocket subscribers 
    """
    while True:
        data = copy.deepcopy(drone.get_current_state())
        # append latest queried speed and wifi signal
        data["other"] = {"speed": drone.get_saved_speed(), "wifi": drone.get_saved_wifi()}
        socketio.emit('dronestate', data) 
        socketio.sleep(DRONE_STATE_TRANSFER_RATE)   

def process_video_frame(app):   
    """
    frame processing should happen in this loop, currently the function 
    forwards frames downstream to websocket subscribers
    """ 
    while True:
        try:
            if(time.time() - drone.last_communication_timestamp() < 0.5):
                socketio.emit('video', drone.process_frame(), engineio_logger=False, logger=False )
            else:
                socketio.sleep(1)
        except Exception as e: 
            print(e)
        socketio.sleep(1/VIDEO_TRANSFER_FRAME_RATE)