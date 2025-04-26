import re
from opensearchpy import OpenSearch
from datetime import datetime
from config.settings import Config

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
            index=Config.INDEX_NAME,
            body={
                "size": 1,
                "sort": [{"post_date": {"order": "desc"}}],
                "_source": ["ID", "title", "guid", "post_date"]
            }
        )

        hits = response.get("hits", {}).get("hits", [])
        if not hits:
            return {"message": "No articles found."}, 404

        article = {}
        article["ID"] = hits[0]["_source"].get("ID")
        article["title"] = hits[0]["_source"].get("title")
        article["url"] = hits[0]["_source"].get("guid")
        article["date"] = hits[0]["_source"].get("post_date")



        return {"latest_article": article}, 200

    except Exception as e:
        return {"error": str(e)}, 500
