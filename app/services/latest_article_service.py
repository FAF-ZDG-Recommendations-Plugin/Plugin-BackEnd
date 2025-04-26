import re
import json
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch
from datetime import datetime
from config.settings import Config


# Load embedding model
print("loading model")
model_name = "paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(model_name)

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

def get_latest_article():
    """
    Retrieves the most recent article from the 'articles' index based on post_date.
    """
    try:
        response = client.search(
            index="articles",
            body={
                "size": 1,
                "sort": [{"post_date": {"order": "desc"}}],
                "_source": ["ID", "title", "guid", "post_date"]
            }
        )

        hits = response.get("hits", {}).get("hits", [])
        if not hits:
            return {"message": "No articles found."}, 404

        article = hits[0]["_source"]
        article["_id"] = hits[0]["_id"]
        article["post_date"] = datetime.strptime(article["post_date"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
        article["title"] = re.sub(r'<[^>]+>', '', article["title"])  # Remove HTML tags from title



        return {"latest_article": article}, 200

    except Exception as e:
        return {"error": str(e)}, 500
