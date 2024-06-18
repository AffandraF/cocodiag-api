import io
import uuid
import logging
from PIL import Image
from firebase_admin import storage
from flask import jsonify

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_image(image_file, user_id, path):    
    try:
        image = Image.open(io.BytesIO(image_file.read()))
        image.verify()
        image = Image.open(io.BytesIO(image_file.read()))
        image_file.seek(0)
    except (IOError, SyntaxError) as e:
        logging.error(f"File is not a valid image: {str(e)}")
        return jsonify({'error': 'Invalid image file'}), 400

    image_filename = f"{uuid.uuid4()}-{image_file.filename}"
    firebase_bucket = storage.bucket('cocodiag.appspot.com')
    blob = firebase_bucket.blob(f"{path}/{user_id}/{image_filename}")
    blob.upload_from_file(image_file, content_type=image_file.content_type)
    image_url = blob.public_url  
  
    return image_url