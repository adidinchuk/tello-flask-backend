import os

SECRET_KEY = os.environ.get("SECRET")
CACHE_TYPE = "SimpleCache"
CACHE_DEFAULT_TIMEOUT = 300