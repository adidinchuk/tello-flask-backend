
import cv2
import base64
import logging
import time
import atexit
import collections
import os
import json
from .structs import Rect, Point, RC_Command, Automation_Options
import av
from apscheduler.schedulers.background import BackgroundScheduler
from ...development.DJITelloPy.djitellopy import Tello
from .vision import Vision

#maximum time the server will wait for a read response from the drone (ms)
COMMAND_TIMEOUT_THRESHOLD = 1
STATUS_JOBS_PERIOD = 3
CONNECTION_MANAGER_JOB_PERIOD = 15
CONNECTION_TIMEOUT_THRESHOLD = 5

class TelloDrone(Tello):
    """
    Drone object inheriting from the DJI Tello library 
    Provides a few overwrites and useful methods
    """

    LOGGER = logging.getLogger('app')
    _job_scheduler = BackgroundScheduler()
    
    def __init__(self):
        self._automation_controller = MotionController(target=self)
        super().__init__()    
        # give initialization some time to complete
        self._connect_to_drone()
        #launch monitoring jobs
        self._job_scheduler.add_job(func=self.connection_manager_job, trigger="interval", seconds=CONNECTION_MANAGER_JOB_PERIOD)
        self._job_scheduler.add_job(func=self.poller_job, trigger="interval", seconds=STATUS_JOBS_PERIOD)
        self._job_scheduler.start()        
        atexit.register(lambda: self._job_scheduler.shutdown())

    def process_frame(self, file_type='.jpg', encoding='utf-8'):
        """
        processes the most frame sent by the Tello drone
        returns a frame in the format dictated by file_type & encoding
        if automation is set, the frame will be passed through the automation pipe
        """
        raw_frame = self.get_frame_read().frame
        color_adjusted_frame = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2RGB)
        processed_frame = self._automation_controller.process_frame(color_adjusted_frame)
        jpg_frame = cv2.imencode(file_type, processed_frame)[1].tobytes()                   
        return base64.encodebytes(jpg_frame).decode(encoding)

    def set_automation_target(self, value):
        """
        Update the automation state for the drone. Currently only follow single face or
        multiple faces automations are supported
        """
        if(value in Automation_Options):
            self._automation_controller.automation_target = value
            return True
        else:
            raise ValueError('Invalid automation option.')

    def _connect_to_drone(self):
        """ Drone initialization, including resetting the video stream """
        response = self.process_instructions('command', data=None, response_required=True)
        if response.lower() == 'ok':
            time.sleep(0.1)
            self.LOGGER.info("Connection with drone has been established.")
            self.process_instructions('streamoff', data=None, response_required=True)
            time.sleep(0.1)
            response = self.process_instructions('streamon', data=None, response_required=True)
            if response.lower() == 'ok':
                self.LOGGER.info("The drone's video stream has been opened.")
                self._connected = True

    def process_instructions(self, command, data, response_required=False):
        """ 
        This function should forwards commands to the drone. 
        Validation and translation is done using the build_drone_command() function
        """
        rawInstructions = build_drone_command(command, data)       
        return self.forward_raw_instructions(rawInstructions, response_required);

    def forward_raw_instructions(self, rawInstructions, response_required=False):
        """
        pass the send command to the parent Tello object
        """
        if response_required:
            return self.send_command_with_return(rawInstructions, timeout=COMMAND_TIMEOUT_THRESHOLD)
        else :
            return self.send_command_without_return(rawInstructions)

    def poller_job(self):
        """ Poll tello for speed & wifi data and cache the values """
        if(self.connected()):
            self.query_speed()
            self.query_wifi_signal_noise_ratio()


    def connected(self):
        """ Return the drone's connection status using the last recieved state packet """
        if(len(self.get_current_state()) == 0):
            self._connected = False                   
        elif(time.time() - self.get_current_state()['timestamp'] > CONNECTION_TIMEOUT_THRESHOLD):
            self._connected = False      
        return self._connected
    
    def connection_manager_job(self):
        """ Track connection state and re-connect with drone if required """
        if(not self.connected()):
            self.LOGGER.info('Attempting to re-establish communication with the drone.')
            self._connect_to_drone()

    def instruction_route_wrapper(self, instruction, data):
        """ 
        Wrapper function used for forwarding API requests to the physical drone
        instruction string must match a drone command and the data json must have an appropriate 
        payload format (if required)
        """
        response = self.process_instructions(instruction, data, response_required=True)
        if response.lower() == 'ok':
            return True
        raise RuntimeError(response)

# load the command options object
with open(os.path.join(os.path.dirname(__file__), '../metadata/commands.json'), 'r') as f:
  SCHEMA = json.load(f)

HANDSHAKE_COMMAND = 'command'
WIFI_GET_COMMAND = 'wifi?'
SPEED_GET_COMMAND = 'speed?'

COMMAND_TIMEOUT_THRESHOLD = 1 # maximum time the server will wait for a read response from the drone (ms)
RECONNECTION_ATTEMPT_PERIOD = 10000 # reconnection attempt frequency (ms)
COMMAND_RESET_PERIOD = 2000 # permitted drone silence preiod before the connection is considered lost (ms)
AUTOMATION_CYCLE = 30 # frequency of the cycle that sends movement commands to the drone when in automation mode (ms)
DRONE_STATE_THROTTLE = 1000 # dictates how often drone state data should be sent downstream to consuming systems (ms)

PERMITTED_COMMANDS = SCHEMA["control"] + SCHEMA["read"] + SCHEMA["set"]

def build_drone_command(command, data):
    """Validates and composes the raw drone command"""

    def process_sub_command(commandComponenet, commandSchema):
        """
        Recursive function to translate and validate incoming 
        instructions into tellow command using a commandSchema document
        """
        resultString = ''
        if ("values" in commandSchema):
            if (commandComponenet >= commandSchema["values"]["min"] and commandComponenet <= commandSchema["values"]["max"]):
                resultString = commandComponenet
            else:
                raise ValueError('Provided command value is outside the allowed threshold.')
        else:
            for element in commandSchema:
                resultString += ' ' + str(process_sub_command(commandComponenet[element], commandSchema[element]))
        return resultString

    if (not command in PERMITTED_COMMANDS):
        print('Command REJECTED as it is not on the approved list.')
        raise ValueError('Command REJECTED as it is not on the approved list.')
    
    constructedCommand = command

    if (data == None):
        return constructedCommand

    if (command in SCHEMA["valueThresholds"]):
        constructedCommand += ' ' + process_sub_command(data, SCHEMA["valueThresholds"][command])
    
    return constructedCommand

from . import pid

VIDEO_WIDTH = 960
VIDEO_HEIGHT = 720
SCREEN_CENTER = Point(VIDEO_WIDTH / 2, VIDEO_HEIGHT / 2)
THRESHOLD_HEIGHT = 250
THRESHOLD_WIDTH = 250

THRESHOLD_POSITION = Rect(int(SCREEN_CENTER.x - THRESHOLD_WIDTH/2), int(SCREEN_CENTER.y - THRESHOLD_HEIGHT/2), THRESHOLD_WIDTH, THRESHOLD_HEIGHT)


class MotionController():
    """
    Object resposible for the automation of the drone
    """

    def __init__(self, target):
        self._control_object = target
        self.automation_target = Automation_Options.NILL
        self._pid_z = pid.PIDController(kP=0.25, kI=0, kD=0.1, saturation_limit_max=50, saturation_limit_min=-50)
        self._pid_r = pid.PIDController(kP=0.3, kI=0, kD=1, saturation_limit_max=50, saturation_limit_min=-50)
        self._set_next_insturction(0,0,0,0)

    def _update_motion_values(self, target):
        """
        computes the error values and updates motion insturctions using PID controllers
        """
        x, y, z, r = 0, 0, 0, 0 # zero out rc command values
        if(self.is_active() and target != None):
            error = target.distance_from_point(SCREEN_CENTER)
            if(abs(error.y) > THRESHOLD_HEIGHT / 2):
                z = self._pid_z.generate_value(error.y)
            if(abs(error.x) > THRESHOLD_WIDTH / 2):
                r = self._pid_r.generate_value(-error.x)
        self._control_object.process_instructions('rc', {"a" : x, "b" : y, "c" : z, "d": r }, response_required=False)
        self._set_next_insturction(x, y, z, r)
        return True

    def _set_next_insturction(self, x, y, z, r):
        self._next_automation_instruction = RC_Command(x, y, z, r)

    def get_next_instruction(self):
        return self._next_automation_instruction

    def is_active(self):
        return True if self.automation_target != Automation_Options.NILL else False

    def process_frame(self, frame):
        """
        updates the automation model with the provided video frame
        to be updated with more automation options
        """
        if self.is_active() :
            target = Vision.track_faces(frame, max_targets=self.automation_target)     
            frame = Vision.draw_identifier(frame, THRESHOLD_POSITION)
            self._update_motion_values(target)
        return frame
