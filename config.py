import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get("SECRET")
API_IP_ADDRESS = os.environ.get("API_IP_ADDRESS")
API_PORT = os.environ.get("API_PORT")
CACHE_TYPE = "SimpleCache"
CACHE_DEFAULT_TIMEOUT = 300