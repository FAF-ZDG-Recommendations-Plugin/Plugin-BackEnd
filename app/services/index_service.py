import re
import json
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch
from datetime import datetime
from config.settings import Config


# Load embedding model
print("loading model")
model_name = "all-MiniLM-L6-v2"
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

# Define embedding dimension
EMBEDDING_DIM = model.encode(["Sample sentence"])[0].shape[0]

# Define OpenSearch index mapping
index_body = {
    "settings": {
        "index": {"knn": True, "knn.algo_param.ef_search": 100}
    },
    "mappings": {
        "properties": {
            "ID": {"type": "long"},
            "title": {"type": "text"},
            "guid": {"type": "keyword"},  # Store URL as a keyword
            "post_date": {
                "type": "date",
                "format": "strict_date_optional_time||yyyy-MM-dd HH:mm:ss"
            },
            "embedding": {
                "type": "knn_vector",
                "dimension": EMBEDDING_DIM,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "nmslib",
                    "parameters": {"ef_construction": 128, "m": 24}
                }
            }
        }
    }
}

print("connected to opensearch")

'''
# Create index if it doesn't exist
if not client.indices.exists(index=INDEX_NAME):
    response = client.indices.create(index=INDEX_NAME, body=index_body)
    print(f"Index '{INDEX_NAME}' created:", response)
else:
    print(f"Index '{INDEX_NAME}' already exists.")
'''

def post_already_indexed(post_id):
    """Check if a post with the given ID is already in OpenSearch."""
    return client.exists(index=Config.INDEX_NAME, id=post_id)

    


def index_article(post):
    # Ensure required fields exist
    if "id" not in post or "content" not in post or "post_date" not in post:
        return {"error": "Missing required fields: id, content, post_date"}

    # Convert post_date to ISO 8601 format
    try:
        post["post_date"] = datetime.strptime(post["post_date"], "%Y-%m-%d %H:%M:%S").isoformat()
    except ValueError:
        return {"error": "Invalid date format, expected 'YYYY-MM-DD HH:MM:SS'"}

    # Check if the post is already indexed
    if post_already_indexed(post["id"]) and post["update"] == "false":
        # If the post is already indexed and not marked for update, skip indexing  
        return {"message": "Post already indexed"}
    elif post["update"] == "true":
        # If the post is marked for update, update the existing document
        post["embedding"] = model.encode(post["content"]).tolist()
        res = client.update(index=Config.INDEX_NAME, id=post["id"], body={"doc": post}, refresh=True)
        return {"message": "Post updated successfully", "opensearch_response": res}


    # Generate embedding
    post["embedding"] = model.encode(post["content"]).tolist()

    # Index into OpenSearch
    res = client.index(index=Config.INDEX_NAME, id=post["id"], body=post, refresh=True)

    return {"message": "Post indexed successfully", "opensearch_response": res}