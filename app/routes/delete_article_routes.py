from flask import Blueprint, request, jsonify
from app.services.delete_article_service import delete_article

delete_bp = Blueprint('delete', __name__)

@delete_bp.route('/delete', methods=['POST'])
def delete():
    data = request.get_json()
    response = delete_article(data)

    return jsonify(response)