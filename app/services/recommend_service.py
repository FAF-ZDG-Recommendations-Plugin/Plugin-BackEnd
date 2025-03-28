from datetime import datetime
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch
from flask import jsonify
from config.settings import Config

print("Loading model...")
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

def recommend_articles(data):
    """Find similar articles with optional date range filtering."""
    
    # Validate input
    if "query_text" not in data or not isinstance(data["query_text"], str):
        return {"error": "Missing or invalid 'query_text' parameter"}, 400
    
    if "top_k" not in data or not isinstance(data["top_k"], int):
        return {"error": "Missing or invalid 'top_k' parameter"}, 400

    # Generate embedding for query
    query_embedding = model.encode([data["query_text"]])[0].tolist()

    # Build the base query
    query_body = {
        "size": data["top_k"],  # Limit results
        "query": {
            "bool": {
                "must": [
                    {"knn": {  # KNN search for similar embeddings
                        "embedding": {
                            "vector": query_embedding,
                            "k": data["top_k"]
                        }
                    }}
                ]
            }
        },
        "_source": ["ID", "title", "guid", "post_date"]  # Return URL + date
    }

    # Add a date range filter if specified
    date_filter = {"range": {"post_date": {}}}
    if "start_date" in data and data["start_date"]:
        try:
            date_filter["range"]["post_date"]["gte"] = datetime.strptime(data["start_date"], "%Y-%m-%d").isoformat()
        except ValueError:
            return {"error": "Invalid start_date format, expected YYYY-MM-DD"}, 400

    if "end_date" in data and data["end_date"]:
        try:
            date_filter["range"]["post_date"]["lte"] = datetime.strptime(data["end_date"], "%Y-%m-%d").isoformat()
        except ValueError:
            return {"error": "Invalid end_date format, expected YYYY-MM-DD"}, 400

    if date_filter["range"]["post_date"]:
        query_body["query"]["bool"]["filter"] = [date_filter]

    try:
        response = client.search(index=Config.INDEX_NAME, body=query_body)
    except Exception as e:
        return {"error": str(e)}, 500  # Return error as JSON with 500 status

    # Process results
    results = []
    for hit in response.get("hits", {}).get("hits", []):
        results.append({
            "ID": hit["_source"].get("ID"),
            "title": hit["_source"].get("title"),
            "url": hit["_source"].get("guid"),  # Return URL
            "date": hit["_source"].get("post_date"),  # Include date
            "score": hit["_score"]
        })

    if not results:
        return {"message": "No articles found."}, 200

    return results, 200
