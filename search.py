from datetime import datetime
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch
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


def search_similar_articles(query_text, top_k=5, start_date=None, end_date=None):
    """Find similar articles with optional date range filtering."""
    query_embedding = model.encode([query_text])[0].tolist()

    # Build the base query
    query_body = {
        "size": top_k,  # Limit results
        "query": {
            "bool": {
                "must": [
                    {"knn": {  # KNN search for similar embeddings
                        "embedding": {
                            "vector": query_embedding,
                            "k": top_k
                        }
                    }}
                ]
            }
        },
        "_source": ["ID", "title", "guid", "post_date"]  # Return URL + date
    }

    # Add a date range filter if specified
    if start_date or end_date:
        date_filter = {"range": {"post_date": {}}}
        if start_date:
            date_filter["range"]["post_date"]["gte"] = start_date
        if end_date:
            date_filter["range"]["post_date"]["lte"] = end_date
        query_body["query"]["bool"]["filter"] = [date_filter]

    response = client.search(index=INDEX_NAME, body=query_body)
    
    results = []
    for hit in response["hits"]["hits"]:
        print(hit)

        '''results.append({
            "ID": hit["_source"]["ID"],
            "title": hit["_source"]["title"],
            "url": hit["_source"]["guid"],  # Return URL
            "date": hit["_source"]["post_date"],  # Include date
            "score": hit["_score"]
        })'''

    return results


query = '''

Consumatorii din capitală vor achita mai mult pentru apă și canalizare. Agenția Națională pentru Reglementare în Energetică (ANRE) a aprobat, în cadrul ședinței publice de marți, 18 martie, noile tarife pentru serviciul public de alimentare cu apă, canalizare și epurare a apelor uzate prestate de S.A. „Apă-Canal Chișinău”.

Conform unui comunicat de presă emis de ANRE, decizia vine în urma unei analize detaliate realizate de ANRE asupra cererii înaintate de operator și a factorilor economici actuali care influențează costurile de operare și întreținere a infrastructurii sistemului de alimentare cu apă și canalizare. Astfel, consumatorii casnici vor achita cu 3,65 lei mai mult pentru alimentarea cu apă potabilă și canalizare.

Noile tarife aprobate:

    12,99 lei/m3 pentru alimentarea cu apă potabilă (creștere de 2,20 lei/m³ față de tariful actual de 10,79 lei/m³);
    12,23 lei/m3 pentru alimentarea cu apă tehnologică (creștere de 4,12 lei/m³ față de tariful actual de 8,11 lei/m³);
    5,63 lei/m3 pentru serviciul de canalizare și epurare a apelor uzate pentru consumatorii casnici  (creștere de 1,45 lei/m³ față de tariful actual de 4,17 lei/m³);
    10,16 lei/m3 pentru serviciul de canalizare și epurare a apelor uzate pentru consumatorii noncasnici  (tarif menținut la același nivel ca în prezent);
    4,22 lei/m3 pentru producerea și transportarea apei în vederea redistribuirii (creștere de 0,81 lei/m³ față de tariful actual de 3,41 lei/m³).

De ce au fost ajustate tarifele?

    „Actualizarea tarifelor este determinată de necesitatea acoperirii costurilor reale ale operatorului în condițiile creșterii generale a prețurilor și pentru asigurarea funcționării continue și eficiente a sistemului public de alimentare cu apă și de canalizare”, a transmis ANRE.

Cheltuielile de operare, întreținere și reparații ale S.A. „Apă-Canal Chișinău” sunt influențate de următorii factori economici și tehnici:

    Creșterea cheltuielilor de energie electrică necesară pentru captarea, tratarea și transportul apei.
    Volumul pierderilor de apă și consumului tehnologic, la un nivel de aproximativ 27% din volumul total captat, în condițiile unei infrastructuri cu un grad înalt de uzură, care necesită lucrări de modernizare.
    Indicele prețurilor de consum prognozat pentru anul 2025 de 4,6%, care influențează costurile pentru materiale, servicii și alte cheltuieli operaționale.

Totodată, tarifele solicitate inițial de operator au fost reduse de ANRE, fiind acceptate doar „cheltuielile strict justificate, pentru a proteja interesele consumatorilor și pentru a evita încărcarea excesivă a facturilor”.

Astfel, venitul reglementat pentru anul 2025 a fost diminuat cu circa 109 milioane lei față de solicitarea operatorului, prin excluderea unor „cheltuieli nejustificate sau neconforme cu metodologia în vigoare (precum reevaluarea unor mijloace fixe și alte ajustări tehnice)”.

Tarifele anterioare au fost aprobate în octombrie 2023 și au rămas nemodificate până în prezent. Noile tarife vor intra în vigoare la data publicării deciziei ANRE în Monitorul Oficial al Republicii Moldova.

'''
similar_articles = search_similar_articles(query, top_k=10,start_date="2025-01-01")

for article in similar_articles:
    print(f"Title: {article['title']}, URL: {article['url']}, Date: {article['date']}, Score: {article['score']}")
