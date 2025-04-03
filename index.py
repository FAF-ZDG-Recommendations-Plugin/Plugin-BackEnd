'''
This code was used to index the articles in the OpenSearch cluster.
'''


import re
import json
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch
from bs4 import BeautifulSoup
from html import unescape

# Load embedding model
print("loading model")
model_name = "all-MiniLM-L6-v2"
model = SentenceTransformer(model_name)

# OpenSearch connection
print("getting opensearch client")
CLUSTER_URL = 'https://localhost:9200'
USERNAME = 'admin'
PASSWORD = 'admin'
INDEX_NAME = "articles"

def get_client(cluster_url=CLUSTER_URL, username=USERNAME, password=PASSWORD):
    """Establish OpenSearch connection."""
    return OpenSearch(
        hosts=[cluster_url],
        http_auth=(username, password),
        verify_certs=False
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

def clean_article_content(raw_content):
    # Remove WordPress comments (e.g., <!-- wp:paragraph -->)
    raw_content = re.sub(r'<!--.*?-->', '', raw_content, flags=re.DOTALL)
    
    # Parse HTML content
    soup = BeautifulSoup(raw_content, "html.parser")
    
    # Remove all links but keep their text
    for a in soup.find_all("a"):
        a.replace_with(a.text)  # Replace the link with just the visible text
    
    # Extract text without any tags
    cleaned_text = soup.get_text(separator=" ", strip=True)

    for char in ["\r", "\n", "\t","\r\n","\n\r", "\n\r\n", "\r\n\n", "\r\r", "\n\n", "\t\t"]:
        cleaned_text = cleaned_text.replace(char, " ")
    
    return cleaned_text




# Create index if it doesn't exist
if not client.indices.exists(index=INDEX_NAME):
    response = client.indices.create(index=INDEX_NAME, body=index_body)
    print(f"Index '{INDEX_NAME}' created:", response)
else:
    print(f"Index '{INDEX_NAME}' already exists.")

# Read and parse .sql file
SQL_FILE_PATH = "../zdg_db_backup.sql"


def post_already_indexed(post_id):
    """Check if a post with the given ID is already in OpenSearch."""
    query_body = {
        "query": {
            "term": {"ID": post_id}
        }
    }
    
    response = client.count(index=INDEX_NAME, body=query_body)
    return response["count"] > 0  # If count > 0, post is already indexed


from datetime import datetime

def extract_posts(sql_file_path):
    posts = []
    post_pattern = re.compile(
        r"\(\s*(\d+),\s*(\d+),\s*'([\d\- :]+)',\s*'([\d\- :]+)',\s*'(.*?)',\s*'(.*?)',\s*'(.*?)',"
        r"\s*'(\w+)',\s*'(\w+)',\s*'(\w+)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)',"
        r"\s*'([\d\- :]+)',\s*'([\d\- :]+)',\s*'(.*?)',\s*(\d+),\s*'([^']*)',\s*(\d+),\s*'([^']*)',"
        r"\s*'([^']*)',\s*(\d+)\s*\)"
    )

    with open(sql_file_path, "rb") as file:  # Read in binary mode
        for line in file:
            try:
                decoded_line = line.decode("utf-8")  # Try UTF-8
            except UnicodeDecodeError:
                decoded_line = line.decode("latin-1", errors="replace")  # Fallback to Latin-1

            matches = post_pattern.findall(decoded_line)
            for match in matches:
                post = {
                    "id": int(match[0]),
                    "post_author": int(match[1]),
                    "post_date": match[2],
                    "post_date_gmt": match[3],
                    "content": match[4],
                    "title": match[5],
                    "excerpt": match[6],
                    "status": match[7],
                    "comment_status": match[8],
                    "ping_status": match[9],
                    "password": match[10],
                    "post_name": match[11],
                    "to_ping": match[12],
                    "pinged": match[13],
                    "modified": match[14],
                    "modified_gmt": match[15],
                    "filtered_content": match[16],
                    "parent": int(match[17]),
                    "guid": match[18],  # URL of the article
                    "menu_order": int(match[19]),
                    "post_type": match[20],
                    "mime_type": match[21],
                    "comment_count": int(match[22]),
                }
                
                # Exclude empty content posts
                if not post["content"].strip():
                    continue

                # Ignore everything that isn't a full published article
                if post["status"] != "publish" and post["post_type"] != "post":
                    continue

                if post["guid"].startswith("http://a.") or post["guid"].startswith("https://a."):
                    post["guid"] = post["guid"].replace("://a.", "://", 1)

                # Convert post_date to ISO 8601 format (if not already)
                try:
                    post["post_date"] = datetime.strptime(post["post_date"], "%Y-%m-%d %H:%M:%S").isoformat()
                except ValueError:
                    print(f"Skipping post with invalid date: {post['post_date']}")
                    continue  # Skip invalid date formats

                # Check if the post is already indexed
                if post_already_indexed(post['id']):
                    print(f"Skipping already indexed post ID {post['id']}")
                    continue  # Skip already indexed posts

                clean_text = clean_article_content(post["content"])

                post["embedding"] = model.encode(clean_text).tolist()  # Generate embedding

                post_to_index = {
                    "ID": post["id"],
                    "title": post["title"],
                    "guid": post["guid"],
                    "post_date": post["post_date"],
                    "embedding": post["embedding"]
                }

                res = client.index(
                    index=INDEX_NAME,
                    id=post["id"],  # Set the document ID to match the post ID
                    body=post_to_index,
                    refresh=True
                )
                print(f"Indexed from: {post['post_date']} with URL: {post['guid']}")
                print(f"Indexed post ID {post['id']} with title: {post['title']}")
                


extract_posts(SQL_FILE_PATH)
