import os
from dotenv import load_dotenv

#Function for enviroment variables
load_dotenv()

# General Settings
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
ENV = os.getenv('FLASK_ENV', 'development')

# MongoDB Settings
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/delivery_app')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'delivery_app')

# Firebase Settings
FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH', 'deliversurimbo-firebase-adminsdk-fbsvc-e7d73aeff9.json')

# JWT Setting
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # 24 hours by default

# Setting Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# prefix for our api
API_PREFIX = '/api'