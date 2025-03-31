# **News Article Recommendation System**  

🚀 **A Flask-based API that indexes and recommends news articles using OpenSearch and Sentence Transformers.**  

## **📌 Features**
✅ **Indexing** – Store articles with embeddings for fast recommendations.  
✅ **Searching** – Retrieve relevant articles using similarity search.  
✅ **Updating** – Supports re-indexing articles when updated.  
✅ **Dockerized** – Easily deploy using Docker and Docker Compose.  
✅ **REST API** – Provides endpoints for indexing, searching, and managing articles.  

---

## **🛠️ Setup & Installation**
### **1️⃣ Clone the Repository**  
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### **2️⃣ Configure Environment Variables**  
Create a `.env` file in the project root

### **3️⃣ Run with Docker**  
```bash
docker-compose up --build
```

### **4️⃣ Access the API**  
Once running, the API will be available at:  
```
http://localhost:5000
```

---

## **📝 API Endpoints**  
### **🚀 Test Connection**  
```http
GET /test
```
📌 **Response:** `{ "status": "ok" }`  

### **🔍 Check OpenSearch Connection**  
```http
GET /test_opensearch
```
📌 **Response:** `{ "status": "connected" }`  

### **📰 Index an Article**  
```http
POST /index
```
📌 **Request Body:**  
```json
{
    "id": 10000,
    "title": "OpenSearch Indexing Test",
    "guid": "https://example.com/article/1",
    "post_date": "2025-03-24 15:30:00",
    "update":"false",
    "content": "This is a test article content for OpenSearch indexing."
}
```
📌 **Response:** `{ "message": "Article indexed successfully" }`  

### **📌 Search for Recommendations**  
```http
POST /recommend
```
📌 **Request Body:**  
```json
{
    "query_text": "This is a test article content for OpenSearch indexing.Updated once",
    "top_k": 5,
    "start_date": "2024-01-01",
    "end_date": ""
}
```
📌 **Response:** `{ "articles": [...] }`  

---

## **🛠️ Technologies Used**  
- **Flask** – Backend API  
- **OpenSearch** – Indexing & Search  
- **Sentence Transformers** – AI-powered similarity search  
- **Docker & Docker Compose** – Containerized deployment   

---

## **📜 License**  
📝 MIT License – Free to use and modify.  
