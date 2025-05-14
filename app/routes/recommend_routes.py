from flask import Blueprint, request, jsonify
from app.services.recommend_service import recommend_articles
from opensearchpy import OpenSearch
from config.settings import Config
from utils.auth_utils import basic_auth_required

recommend_bp = Blueprint('recommend', __name__)


def get_client():
    """Establish OpenSearch connection securely using environment variables."""
    return OpenSearch(
        hosts=[{"host": Config.OPENSEARCH_HOST, "port": Config.OPENSEARCH_PORT}],
        http_auth=(Config.OPENSEARCH_USERNAME, Config.OPENSEARCH_PASSWORD),
        use_ssl=True,
        verify_certs=False,  # This should be True in production
        ssl_show_warn=False
    )

client = get_client()

@recommend_bp.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "ok"}), 200

@recommend_bp.route('/test_opensearch', methods=['GET'])
def test_opensearch():
    try:
        client.info()  # Check if OpenSearch responds
        return jsonify({"status": "connected"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@recommend_bp.route('/recommend', methods=['POST'])
@basic_auth_required
def recommend():
    data = request.get_json()
    response = recommend_articles(data)
    return jsonify(response)
