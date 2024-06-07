from flask import Blueprint, request, jsonify
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_jwt_extended.exceptions import JWTError
from google.auth.transport import requests as grequests
from google.oauth2 import id_token
from config.firebase_config import auth, db
import logging

auth_bp = Blueprint('auth_bp', __name__)

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
    token = data.get('token')

    try:
        # Verify ID token
        decoded_token = id_token.verify_oauth2_token(token, grequests.Request())
        user_id = decoded_token['uid']

        # Retrieve user info from Firestore
        user_info_ref = db.collection('users').document(user_id)
        user_info = user_info_ref.get().to_dict()

        # Create access token using Flask-JWT-Extended
        access_token = create_access_token(identity=user_id)

        return jsonify({
            "id": user_id,
            "name": user_info['name'],
            "email": user_info['email'],
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
    except JWTError:
        return jsonify({"message": "Invalid JWT token"}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500