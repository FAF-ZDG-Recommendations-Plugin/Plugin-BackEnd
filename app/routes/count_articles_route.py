from flask import Blueprint, request, jsonify
from app.services.count_articles_service import count_articles

count_bp = Blueprint('count', __name__)

@count_bp.route('/count', methods=['GET'])
def count():
    response = count_articles()

    return jsonify(response)