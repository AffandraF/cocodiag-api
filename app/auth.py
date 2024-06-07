from flask import Blueprint, request, jsonify
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from config.firebase_config import auth, db
from config.secret_manager import access_secret_version
import requests
import logging

auth_bp = Blueprint('auth_bp', __name__)

API_KEY = access_secret_version('cocodiag', 'firebase-web-api', 'latest')

def firebase_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({"message": "Unauthorized"}), 401
        request.user_id = current_user
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
        response = requests.post(f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}", json=payload)
        
        response_data = response.json()

        logging.debug(f"Response Data: {response_data}")

        if 'error' in response_data:
            raise Exception(response_data['error']['message'])

        id_token_str = response_data.get('idToken')
        if not id_token_str:
            raise Exception("ID token is missing in the response")

        # try:
        #     decoded_token = id_token.verify_oauth2_token(id_token_str, grequests.Request())
        #     user_id = decoded_token['uid']
        # except ValueError as e:
        #     logging.error(f"Token verification failed: {e}")
        #     raise Exception("Token verification failed. Check your network connection and ensure the token is valid.")
        
        user_id = response_data.get('localId')

        access_token = create_access_token(identity=user_id)        
        
        user_info_ref = db.collection('users').document(user_id)
        user_info_doc = user_info_ref.get()
        
        if not user_info_doc.exists:
            raise Exception("User not found in Firestore")
        
        user_info = user_info_doc.to_dict()

        return jsonify({
            "id": user_id,
            "name": user_info.get('name'),
            "email": user_info.get('email'),
            "imageProfile": user_info.get('imageProfile'),
            "token": access_token
        }), 200
    except Exception as e:
        logging.error(f"Sign-in error: {e}")
        return jsonify({"message": str(e)}), 400

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
@firebase_auth_required
def protected():
    try:
        return jsonify({"message": f"Hello user {request.user_id}"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500