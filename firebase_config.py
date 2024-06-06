import os
import json
import pyrebase
from google.cloud import secretmanager

def access_secret_version(project_id, secret_id, version_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

PROJECT_ID = "cocodiag"
SECRET_ID = "firebase-config"
VERSION_ID = "latest"

firebase_config_json = access_secret_version(PROJECT_ID, SECRET_ID, VERSION_ID)
firebase_config = json.loads(firebase_config_json)

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()