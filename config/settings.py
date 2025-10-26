import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "opensearch-node1")
    OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", 9200))
    OPENSEARCH_USERNAME = os.getenv("OPENSEARCH_USERNAME", "admin")
    OPENSEARCH_PASSWORD = os.getenv("OPENSEARCH_PASSWORD", "admin")
    OPENSEARCH_USE_SSL = os.getenv("OPENSEARCH_USE_SSL", "False").lower() == "true"
    INDEX_NAME = os.getenv("INDEX_NAME", "articles")
    API_SECRET_KEY = os.getenv("API_SECRET_KEY")

