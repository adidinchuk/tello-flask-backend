from multiprocessing.connection import wait
from .utils import *
import time
from . import drone
import time 
import atexit
from .. import cache
from apscheduler.schedulers.background import BackgroundScheduler

import logging
CONNECTION_TIMEOUT_THRESHOLD = 5
CONNECTION_MANAGER_JOB_PERIOD = 15
STATUS_JOBS_PERIOD = 3

LOGGER = logging.getLogger('app')
job_scheduler = BackgroundScheduler()

def instruction_route_wrapper(instruction, data):
    """ High level wrapper to sending data to the drone, used by rotes """
    try:
        response = process_instructions(instruction, data, response_required=True)
        if response.lower() == 'ok':
            return success_response
        return build_fail_respose(response)
    except ValueError as e:
       return build_fail_respose(str(e))

def process_instructions(command, data, response_required=False):
    """ 
    This function should be called to forward any commands to the drone. 
    It performa validation and translation using the build_drone_command() function
    """
    rawInstructions = ''
    """convert instruciton to raw drone command"""
    try:
        rawInstructions = build_drone_command(command, data)
    except ValueError as e:
        return str(e)
    """push the command onto the drone command queue"""
    return forward_raw_instructions(rawInstructions, response_required);

def forward_raw_instructions(rawInstructions, response_required=False):
    if response_required:
        return drone.send_command_with_return(rawInstructions, timeout=COMMAND_TIMEOUT_THRESHOLD)
    else :
        return drone.send_command_without_return(rawInstructions)

def connected():
    """ Return the drone's connection status using the last recieved state packet """
    if(len(drone.get_current_state()) == 0):
        return False
    elif(time.time() - drone.get_current_state()['timestamp'] > CONNECTION_TIMEOUT_THRESHOLD):
        return False
    return True

def connect_to_drone():
    """ Drone initialization, including resetting the video stream """
    response = process_instructions('command', data=None, response_required=True)
    if response.lower() == 'ok':
        LOGGER.info("Connection with drone has been established.")
        process_instructions('streamoff', data=None, response_required=False)
        time.sleep(0.1)
        process_instructions('streamon', data=None, response_required=False)
        if response.lower() == 'ok':
            LOGGER.info("The drone's video stream has been opened.")

def connection_manager_job():
    """ Track connection state and re-connect with drone if required """
    if(not connected()):
        LOGGER.info('Attempting to re-establish communication with the drone.')
        connect_to_drone()

def wifi_poller_job():
    """ Poll tello for wifi strength data and cache the value """
    if(connected()):
        signal = drone.query_wifi_signal_noise_ratio()
        cache.set('wifi', {"timestamp": time.time(), "data": signal})

def speed_poller_job():
    """ Poll tello for speed data and cache the value """
    if(connected()):
        speed = drone.query_speed()
        cache.set('speed', {"timestamp": time.time(), "data": speed})
       
def init_tello():
    """
    Initialize the connection between Tello and this web application
    """
    connect_to_drone()
    job_scheduler.add_job(func=connection_manager_job, trigger="interval", seconds=CONNECTION_MANAGER_JOB_PERIOD)
    job_scheduler.add_job(func=wifi_poller_job, trigger="interval", seconds=STATUS_JOBS_PERIOD)
    job_scheduler.add_job(func=speed_poller_job, trigger="interval", seconds=STATUS_JOBS_PERIOD)
    job_scheduler.start()
    atexit.register(lambda: job_scheduler.shutdown())