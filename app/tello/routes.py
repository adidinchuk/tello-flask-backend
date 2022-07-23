from .services import *
from flask import request, Blueprint

tello_routes = Blueprint('tello_routes', __name__)

@tello_routes.route('/tello/connect')
def tello_command():
    return instruction_route_wrapper("command", None)

@tello_routes.route('/tello/takeoff', methods = ['GET', 'POST'] )
def tello_takeoff():
    return instruction_route_wrapper("takeoff", None)

@tello_routes.route('/tello/land', methods = ['GET', 'POST'])
def tello_land():
    result = instruction_route_wrapper("land", None)
    return result

@tello_routes.route('/tello/streamon')
def tello_streamon():
    return instruction_route_wrapper("streamon", None)

@tello_routes.route('/tello/rc', methods = ['GET', 'POST'])
def tello_rc():
    process_instructions("rc", request.get_json(), response_required=False)
    return success_response

@tello_routes.route('/tello/emergency', methods = ['GET', 'POST'])
def tello_emergency():
    return instruction_route_wrapper("emergency", None)