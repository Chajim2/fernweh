from flask import request, jsonify
from functools import wraps
from dotenv import load_dotenv
import os
import jwt
from jwt import InvalidTokenError
from datetime import datetime, timedelta, timezone

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-secret-key')
ALGORITHM = 'HS256'


def require_jwt(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json()

        if not data or 'id' not in data:
            return jsonify({'error': 'JWT is missing in request body'}), 401

        token = data['id']

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return f(*args, **kwargs, id=payload['id'], data=data)

        except InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

    return decorated_function


def create_refresh_jwt(payload_data):
    payload_data['exp'] = datetime.now(timezone.utc) + timedelta(hours=2 * 168)
    payload = payload_data.copy()

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


def create_auth_jwt(payload_data):
    payload_data['exp'] = datetime.now(timezone.utc) + timedelta(hours=3)
    payload = payload_data.copy()

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token
