import base64
import requests
from flask import request, jsonify
from functools import wraps

def verify_wp_credentials(username, password):
    """Use WP REST API to validate credentials."""
    url = 'https://zdg.md/wp-json/wp/v2/users/me'
    response = requests.get(url, auth=(username, password))
    return response.status_code == 200

def basic_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith('Basic '):
            return jsonify({"error": "Missing Authorization header"}), 401

        try:
            encoded_credentials = auth.split(' ')[1]
            decoded = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded.split(':', 1)
        except Exception:
            return jsonify({"error": "Invalid Authorization header"}), 401

        if not verify_wp_credentials(username, password):
            return jsonify({"error": "Invalid credentials"}), 403

        return f(*args, **kwargs)
    return decorated
