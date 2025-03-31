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
    "query_text": "Universitatea tehnică a Moldovei",
    "top_k": 5,
    "start_date": "2024-01-01",
    "end_date": ""
}

```
📌 **Response:** 

```
[
    [
        {
            "ID": 1726774,
            "date": "2024-05-28T20:11:16",
            "score": 0.514862,
            "title": "USM amână negocierile de fuziune cu UTM și cere Guvernului „garanții ferme cu privire la finanțarea adecvată a viitoarei instituții”",
            "url": "https://www.zdg.md/?p=1726774"
        },
        {
            "ID": 1727984,
            "date": "2024-06-03T13:08:10",
            "score": 0.49384695,
            "title": "MEC: A fost lansată o amplă campanie de prevenire a corupției în universități",
            "url": "https://www.zdg.md/?p=1727984"
        },
        {
            "ID": 1766369,
            "date": "2024-11-25T18:11:16",
            "score": 0.48641315,
            "title": "„Singura știință este Iisus Hristos”. Narațiunile propagate de Călin Georgescu, candidat la funcția de președinte al României, pe TikTok",
            "url": "https://www.zdg.md/?p=1766369"
        },
        {
            "ID": 1761084,
            "date": "2024-11-01T10:26:53",
            "score": 0.47671726,
            "title": "Universitatea Pedagogică „Ion Creangă” a beneficiat de două granturi în valoare totală de 3,3 milioane de euro",
            "url": "https://www.zdg.md/?p=1761084"
        },
        {
            "ID": 1738841,
            "date": "2024-07-22T10:56:48",
            "score": 0.47523156,
            "title": "Începe sesiunea de admitere la instituțiile de învățământ superior. Cum pot fi depuse dosarele",
            "url": "https://www.zdg.md/?p=1738841"
        }
    ],
    200
]
```

---

## **🛠️ Technologies Used**  
- **Flask** – Backend API  
- **OpenSearch** – Indexing & Search  
- **Sentence Transformers** – AI-powered similarity search  
- **Docker & Docker Compose** – Containerized deployment   

---

## **📜 License**  
📝 MIT License – Free to use and modify.  
