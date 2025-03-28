from opensearchpy import OpenSearch

# OpenSearch connection details
CLUSTER_URL = 'https://localhost:9200'
USERNAME = 'admin'
PASSWORD = 'admin'
INDEX_NAME = "articles"

# Establish OpenSearch connection
client = OpenSearch(
    hosts=[CLUSTER_URL],
    http_auth=(USERNAME, PASSWORD),
    verify_certs=False
)

# Delete all documents from the index
def clear_index(index_name):
    """Deletes all documents from the specified OpenSearch index."""
    response = client.delete_by_query(
        index=index_name,
        body={"query": {"match_all": {}}}
    )
    print(f"Deleted {response['deleted']} documents from index '{index_name}'.")

clear_index(INDEX_NAME)
