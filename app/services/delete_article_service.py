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

def delete_article(data):
    """
    Deletes an article from the 'articles' index using either its title or ID.
    Expects a dictionary with either 'title' or 'ID' key.
    """
    if not isinstance(data, dict):
        return {"error": "Invalid input, expected a JSON object."}, 400

    # Prepare search query
    if "ID" in data:
        search_query = {
            "query": {
                "term": {
                    "ID.keyword": data["ID"]  # Assumes ID is stored as keyword
                }
            }
        }
    elif "title" in data:
        search_query = {
            "query": {
                "match_phrase": {
                    "title": data["title"]
                }
            }
        }
    else:
        return {"error": "Provide either 'ID' or 'title' to delete an article."}, 400

    try:
        # Search for the article(s) to delete
        response = client.search(index="articles", body=search_query)
        hits = response.get("hits", {}).get("hits", [])
        if not hits:
            return {"message": "No matching article found."}, 404

        deleted_ids = []
        for hit in hits:
            article_id = hit["_id"]
            client.delete(index="articles", id=article_id)
            deleted_ids.append(article_id)

        return {"message": f"Deleted {len(deleted_ids)} article(s).", "deleted_ids": deleted_ids}, 200

    except Exception as e:
        return {"error": str(e)}, 500

