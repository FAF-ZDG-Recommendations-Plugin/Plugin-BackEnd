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

def count_articles():
    """Print the total number of articles in the OpenSearch index."""
    global client  # Use the existing OpenSearch client
    
    response = client.count(index=Config.INDEX_NAME)
    return response["count"]