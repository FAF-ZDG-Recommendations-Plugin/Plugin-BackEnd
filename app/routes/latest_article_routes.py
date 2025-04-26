from flask import Blueprint, request, jsonify
from app.services.latest_article_service import get_latest_article

latest_bp = Blueprint('latest', __name__)

@latest_bp.route('/latest', methods=['GET'])
def latest():
    response = get_latest_article()

    return jsonify(response)