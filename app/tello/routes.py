from flask import request, Blueprint
from . import drone
import json

tello_routes = Blueprint('tello_routes', __name__)

success_response = json.dumps({'success':True}), 200, {'ContentType':'application/json'}

def build_fail_respose(msg):
    """
    Basic fail http wrapper function
    """
    return json.dumps({'success':False, "message": msg}), 412, {'ContentType':'application/json'}

@tello_routes.route('/tello/connect')
def tello_command():
    try:
        drone.instruction_route_wrapper("command", None)
        return success_response
    except Exception as e:
        return build_fail_respose(str(e))

@tello_routes.route('/tello/takeoff', methods = ['GET', 'POST'] )
def tello_takeoff():
    try:
        drone.instruction_route_wrapper("takeoff", None)
        return success_response
    except Exception as e:
        return build_fail_respose(str(e))

@tello_routes.route('/tello/land', methods = ['GET', 'POST'])
def tello_land():
    try:
        drone.instruction_route_wrapper("land", None)
        return success_response
    except Exception as e:
        return build_fail_respose(str(e))

@tello_routes.route('/tello/streamon')
def tello_streamon():
    try:
        drone.instruction_route_wrapper("streamon", None)
        return success_response
    except Exception as e:
        return build_fail_respose(str(e))

@tello_routes.route('/tello/rc', methods = ['GET', 'POST'])
def tello_rc():
    try:
        drone.process_instructions("rc", request.get_json(), response_required=True)
        return success_response
    except Exception as e:
        return build_fail_respose(str(e))

@tello_routes.route('/tello/emergency', methods = ['GET', 'POST'])
def tello_emergency():
    try:
        drone.instruction_route_wrapper("emergency", None)
        return success_response
    except Exception as e:
        return build_fail_respose(str(e))

tello_automation_routes = Blueprint('tello_automation_routes', __name__)

@tello_automation_routes.route('/tello/automation/followperson', methods = ['GET', 'POST'] )
def automation_followperson():
    try:
        drone.set_automation_target(1)
        return success_response
    except Exception as e:
        return build_fail_respose(str(e))

@tello_automation_routes.route('/tello/automation/followpersons', methods = ['GET', 'POST'] )
def automation_followpersons():
    try:
        drone.set_automation_target(0)
        return success_response
    except Exception as e:
        return build_fail_respose(str(e))

@tello_automation_routes.route('/tello/automation/clear', methods = ['GET', 'POST'] )
def automation_clear():
    try:
        drone.set_automation_target(None)
        return success_response
    except Exception as e:
        return build_fail_respose(str(e))