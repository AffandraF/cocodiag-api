from flask import Blueprint, request, jsonify
import pyrebase
import jwt
from functools import wraps
from firebase_config import firebase_config, SECRET_KEY

auth_bp = Blueprint('auth_bp', __name__)

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

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
        user = auth.create_user_with_email_and_password(email, password)
        user_id = user['localId']
        db.child("users").child(user_id).set({"name": name, "email": email})
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
        user = auth.sign_in_with_email_and_password(email, password)
        user_id = user['localId']
        user_info = db.child("users").child(user_id).get().val()
        token = jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm='HS256')
        return jsonify({
            "id": user_id,
            "name": user_info['name'],
            "email": user_info['email'],
            "imageProfile": None,
            "token": token
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@auth_bp.route('/protected', methods=['GET'])
@firebase_auth_required
def protected():
    return jsonify({"message": f"Hello user {request.user_id}"}), 200