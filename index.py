import re
import json
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch
from bs4 import BeautifulSoup
from html import unescape
from datetime import datetime

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
            "content": {"type": "text"},  # NEW: Store full article text
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

# Create index if it doesn't exist
if not client.indices.exists(index=INDEX_NAME):
    response = client.indices.create(index=INDEX_NAME, body=index_body)
    print(f"Index '{INDEX_NAME}' created:", response)
else:
    print(f"Index '{INDEX_NAME}' already exists.")

# Clean article content
def clean_article_content(raw_content):
    """Removes HTML tags, scripts, and unnecessary whitespace from article content."""
    raw_content = re.sub(r'<!--.*?-->', '', raw_content, flags=re.DOTALL)  # Remove WP comments
    soup = BeautifulSoup(raw_content, "html.parser")
    
    # Remove links but keep their text
    for a in soup.find_all("a"):
        a.replace_with(a.text)  
    
    cleaned_text = soup.get_text(separator=" ", strip=True)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalize whitespace
    return cleaned_text.strip()

SQL_FILE_PATH = "../zdg_db_backup.sql"

def post_already_indexed(post_id):
    """Check if a post with the given ID is already in OpenSearch."""
    query_body = {"query": {"term": {"ID": post_id}}}
    response = client.count(index=INDEX_NAME, body=query_body)
    return response["count"] > 0  

def is_bogus(title):
    """Check if a title is bogus."""
    return title.strip() == "" or re.fullmatch(r"\d+", title)

def normalize_diacritics(text):
    """Normalize Romanian diacritics in the text."""
    replacements = {
        "ă": "a", "â": "a", "î": "i", "ș": "s", "ț": "t","ţ": "t","ş": "s",
        "Ă": "A", "Â": "A", "Î": "I", "Ș": "S", "Ț": "T","Ţ": "T","Ş": "S",
        "ắ": "a", "ấ": "a", "î́": "i", "ș́": "s", "ț́": "t","ţ́": "t","ş́": "s",
        "Ắ": "A", "Ấ": "A", "Î́": "I", "Ș́": "S", "Ț́": "T","Ţ́": "T","Ş́": "S"
    }
    for diacritic in replacements:
        text = text.replace(diacritic, replacements[diacritic])
    return text

def extract_posts(sql_file_path,start_year=2008):
    post_pattern = re.compile(
        r"\(\s*(\d+),\s*(\d+),\s*'([\d\- :]+)',\s*'([\d\- :]+)',\s*'(.*?)',\s*'(.*?)',\s*'(.*?)',"
        r"\s*'(\w+)',\s*'(\w+)',\s*'(\w+)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)',"
        r"\s*'([\d\- :]+)',\s*'([\d\- :]+)',\s*'(.*?)',\s*(\d+),\s*'([^']*)',\s*(\d+),\s*'([^']*)',"
        r"\s*'([^']*)',\s*(\d+)\s*\)"
    )

    with open(sql_file_path, "rb") as file:
        for line in file:
            try:
                decoded_line = line.decode("utf-8")  
            except UnicodeDecodeError:
                decoded_line = line.decode("latin-1", errors="replace")  

            matches = post_pattern.findall(decoded_line)
            for match in matches:
                post = {
                    "id": int(match[0]),
                    "post_author": int(match[1]),
                    "post_date": match[2],
                    "post_date_gmt": match[3],
                    "content": match[4],  # Full article content
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
                    "guid": match[18],  
                    "menu_order": int(match[19]),
                    "post_type": match[20],
                    "mime_type": match[21],
                    "comment_count": int(match[22]),
                }

                # Convert post_date to ISO 8601 format
                try:
                    post["post_date"] = datetime.strptime(post["post_date"], "%Y-%m-%d %H:%M:%S").isoformat()
                    if post["post_date"] < datetime(year=start_year, month=1, day=1).isoformat():
                        print(f"Skipping post older than {start_year}: {post['post_date']}")
                        continue
                except ValueError:
                    print(f"Skipping post with invalid date: {post['post_date']}")
                    continue 

                # Skip empty or non-article posts
                if not post["content"].strip() or post["status"] != "publish" or post["post_type"] != "post":
                    continue          

                # Ignore posts with empty or bogus titles
                if is_bogus(post["title"]):
                    print(f"Skipping bogus title: {post['title']}")
                    continue


                # Normalize URL
                if post["guid"].startswith("http://a.") or post["guid"].startswith("https://a."):
                    post["guid"] = post["guid"].replace("://a.", "://", 1)


                # Skip already indexed posts
                if post_already_indexed(post['id']):
                    print(f"Skipping already indexed post ID {post['id']}")
                    continue  

                # Clean content
                clean_text = normalize_diacritics(clean_article_content(post["content"]))

                # Generate embedding
                post["embedding"] = model.encode(clean_text).tolist()  

                # Index post
                post_to_index = {
                    "ID": post["id"],
                    "title": post["title"],
                    "guid": post["guid"],
                    "post_date": post["post_date"],
                    "content": clean_text,  # NEW: Store cleaned content
                    "embedding": post["embedding"]
                }

                res = client.index(
                    index=INDEX_NAME,
                    id=post["id"],  
                    body=post_to_index,
                    refresh=True
                )
                print(f"Indexed post from {post['post_date']}")

extract_posts(SQL_FILE_PATH, start_year=2023)
