import json
import pyrebase
import logging
from .secret_manager import access_secret_version

def initialize_firebase():
    try:
        PROJECT_ID = "cocodiag"
        SECRET_ID = "firebase-config"
        VERSION_ID = "latest"

        firebase_config_json = access_secret_version(PROJECT_ID, SECRET_ID, VERSION_ID)
        firebase_config = json.loads(firebase_config_json)

        firebase = pyrebase.initialize_app(firebase_config)
        auth = firebase.auth()
        db = firebase.database()
        
        logging.info("Firebase initialized successfully.")
        return firebase, auth, db

    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        raise
    except pyrebase.pyrebase.PyrebaseException as e:
        logging.error(f"Pyrebase error: {e}")
        raise
    except Exception as e:
        logging.error(f"General error: {e}")
        raise

firebase, auth, db = initialize_firebase()

SECRET_PROJECT_ID = "cocodiag"
SECRET_ID = "jwt-secret-key"
VERSION_ID = "latest"
SECRET_KEY = access_secret_version(SECRET_PROJECT_ID, SECRET_ID, VERSION_ID)