import json
import pyrebase
from google.cloud import secretmanager
import logging

def access_secret_version(project_id, secret_id, version_id):
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logging.error(f"Error accessing secret version: {e}")
        raise

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