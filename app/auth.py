from flask import Blueprint, request, jsonify
import jwt
import requests
from functools import wraps
from google.auth.transport import requests as grequests
from google.oauth2 import id_token
from config.firebase_config import auth, db, SECRET_KEY
from config.secret_manager import access_secret_version
import logging

auth_bp = Blueprint('auth_bp', __name__)

PROJECT_ID = "cocodiag"
SECRET_ID = "firebase-web-api"
VERSION_ID = "latest"

FIREBASE_WEB_API_KEY = access_secret_version(PROJECT_ID, SECRET_ID, VERSION_ID)

def firebase_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token is missing!"}), 403

        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user_id = decoded_token['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 403

        return f(*args, **kwargs)
    
    return decorated_function

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        user_id = user.uid

        db.collection('users').document(user_id).set({
            "name": name,
            "email": email,
            "imageProfile": None
        })

        return jsonify({
            "id": user_id,
            "name": name,
            "email": email,
            "imageProfile": None
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@auth_bp.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        response = requests.post(f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}", data=payload)
        response_data = response.json()

        logging.debug(f"Response Data: {response_data}")

        if 'error' in response_data:
            raise Exception(response_data['error']['message'])

        id_token_str = response_data['idToken']
        
        try:
            decoded_token = id_token.verify_oauth2_token(id_token_str, grequests.Request())
            user_id = decoded_token['uid']
        except ValueError as e:
            logging.error(f"Token verification failed: {e}")
            raise Exception("Token verification failed. Check your network connection and ensure the token is valid.")
        
        token = jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm='HS256')

        user_info_ref = db.collection('users').document(user_id)
        user_info = user_info_ref.get().to_dict()

        return jsonify({
            "id": user_id,
            "name": user_info['name'],
            "email": user_info['email'],
            "imageProfile": user_info.get('imageProfile'),
            "token": token
        }), 200
    except Exception as e:
        logging.error(f"Sign-in error: {e}")
        return jsonify({"message": str(e)}), 400

@auth_bp.route('/protected', methods=['GET'])
@firebase_auth_required
def protected():
    return jsonify({"message": f"Hello user {request.user_id}"}), 200