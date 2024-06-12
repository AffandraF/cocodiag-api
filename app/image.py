from flask import Blueprint, request, jsonify, send_file
from firebase_admin import storage
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import logging
import time
from flask_jwt_extended import jwt_required

image_bp = Blueprint('image_bp', __name__)

@jwt_required()
def get_image():
    img_url = request.args.get('img_url')
    if not img_url:
        return jsonify({'error': 'Image URL not provided'}), 400
    bucket_name = 'cocodiag.appspot.com'

    try:
        firebase_bucket = storage.bucket(bucket_name)
        blob = firebase_bucket.blob(img_url)

        image_data = blob.download_as_bytes()
        image = Image.open(io.BytesIO(image_data))

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format)
        img_byte_arr.seek(0)

        return send_file(img_byte_arr, mimetype=f'image/{image.format.lower()}')
    except Exception as e:
        logging.error(f"Error fetching image: {str(e)}")
        return jsonify({'error': str(e)}), 500