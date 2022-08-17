from flask import Blueprint

app_routes = Blueprint('app_routes', __name__);

@app_routes.route('/test')
def test():
    return "success"

@app_routes.route('/api/info/get')
def get_info():
    return "This end point has not been implemented"