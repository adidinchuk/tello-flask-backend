from ..development.DJITelloPy.djitellopy import Tello
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

drone = Tello()

from .services import *
from .routes import tello_routes

init_tello()

def __del__(self):
    drone.land()
    drone.end()