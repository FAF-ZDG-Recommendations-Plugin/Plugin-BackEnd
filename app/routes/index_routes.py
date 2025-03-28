from flask import Blueprint, request, jsonify
from app.services.index_service import index_article


index_bp = Blueprint('index', __name__)

@index_bp.route('/index', methods=['POST'])
def index():
    data = request.get_json()
    response = index_article(data)

    return jsonify(response)