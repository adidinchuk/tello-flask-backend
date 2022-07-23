from asyncio.windows_events import NULL
import json
import os

success_response = json.dumps({'success':True}), 200, {'ContentType':'application/json'}

HANDSHAKE_COMMAND = 'command'
WIFI_GET_COMMAND = 'wifi?'
SPEED_GET_COMMAND = 'speed?'

"""maximum time the server will wait for a read response from the drone (ms)"""
COMMAND_TIMEOUT_THRESHOLD = 1 
"""reconnection attempt frequency (ms)"""
RECONNECTION_ATTEMPT_PERIOD = 10000
"""permitted drone silence preiod before the connection is considered lost (ms)"""
COMMAND_RESET_PERIOD = 2000
"""frequency of the cycle that sends movement commands to the drone when in automation mode (ms)"""
AUTOMATION_CYCLE = 30
"""dictates how often drone state data should be sent downstream to consuming systems (ms)"""
DRONE_STATE_THROTTLE = 1000
"""drone camera frame size in pixles"""
FRAME_SIZE = [960, 720]

with open(os.path.join(os.path.dirname(__file__), 'metadata/commands.json'), 'r') as f:
  SCHEMA = json.load(f)


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
    

def build_fail_respose(msg):
    """
    Basic fail http wrapper function
    """
    return json.dumps({'success':False, "message": msg}), 412, {'ContentType':'application/json'}