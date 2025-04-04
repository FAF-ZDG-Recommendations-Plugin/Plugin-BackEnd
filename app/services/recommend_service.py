from datetime import datetime
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch
from flask import jsonify
from config.settings import Config
import numpy as np

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
    """Find similar articles with optional keyword filtering and date range filtering."""
    
    # Validate input
    if "query_text" not in data or not isinstance(data["query_text"], str):
        return {"error": "Missing or invalid 'query_text' parameter"}, 400
    
    if "top_k" not in data or not isinstance(data["top_k"], int):
        return {"error": "Missing or invalid 'top_k' parameter"}, 400

    # Generate embedding for query
    query_embedding = model.encode([data["query_text"]])[0].tolist()

    # Start building query
    query_body = {
        "size": data["top_k"]*10,
        "query": {
            "bool": {
                "must": [],
                "should": [],
                "filter": []
            }
        },
        "_source": ["ID", "title", "guid", "post_date", "content"]
    }

    # If mandatory keywords are provided, filter articles containing all keywords
    if "mandatory_kw" in data and isinstance(data["mandatory_kw"], list) and data["mandatory_kw"]:
        keyword_conditions = [{"match": {"content": keyword}} for keyword in data["mandatory_kw"]]
        query_body["query"]["bool"]["must"].extend(keyword_conditions)  # Ensures all must match
    

    
    # If optional keywords are provided, they should boost results but not remove them
    if "optional_kw" in data and isinstance(data["optional_kw"], list) and data["optional_kw"]:
        keyword_conditions = [{"match": {"content": {"query": keyword, "fuzziness": "AUTO"}}} for keyword in data["optional_kw"]]
        query_body["query"]["bool"]["should"].extend(keyword_conditions)

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
        query_body["query"]["bool"]["filter"].append(date_filter)

    try:
        # First search: Retrieve articles matching mandatory/optional keywords (if provided)
        initial_response = client.search(index=Config.INDEX_NAME, body=query_body)
    except Exception as e:
        return {"error": str(e)}, 500  # Return error as JSON with 500 status

    # Extract article IDs and content for second search step
    filtered_articles = initial_response.get("hits", {}).get("hits", [])
    if not filtered_articles:
        return {"message": "No articles found with given keywords."}, 200

    # Retrieve IDs of keyword-matching articles
    matching_article_ids = [article["_id"] for article in filtered_articles]

    # Build KNN query for similarity search within the filtered articles
    knn_query_body = {
        "size": data["top_k"],
        "query": {
            "bool": {
                "must": [
                    {"terms": {"_id": matching_article_ids}},  # Search only in the previously found articles
                    {"knn": {  # KNN search for similar embeddings
                        "embedding": {
                            "vector": query_embedding,
                            "k": 1000
                        }
                    }}
                ]
            }
        },
        "_source": ["ID", "title", "guid", "post_date", "embedding"]
    }
    

    try:
        # Second search: Perform semantic similarity search within keyword-matching articles
        response = client.search(index=Config.INDEX_NAME, body=knn_query_body)
    except Exception as e:
        return {"error": str(e)}, 500

    # Process final results
    results = []
    for hit in response.get("hits", {}).get("hits", []):
        article_embedding = hit["_source"].get("embedding")
        
        if article_embedding is None:
            print(f"Skipping article {hit['_id']} due to missing embedding.")
            print(f"Embedding: {article_embedding}")
            distance = None

        try:
            distance = float(np.linalg.norm(np.array(query_embedding) - np.array(article_embedding)))
        except Exception as e:
            print(f"Error computing distance: {e}")
            distance = None

        results.append({
            "ID": hit["_source"].get("ID"),
            "title": hit["_source"].get("title"),
            "url": hit["_source"].get("guid"),
            "date": hit["_source"].get("post_date"),
            "score": hit["_score"],
            "actual_distance": distance
        })

    if not results:
        return {"message": "No articles found."}, 200

    return results, 200
