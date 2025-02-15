import os
import json
import time
import weaviate
import nltk
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer, util

# ==============================================================
# CONFIGURATION
# ==============================================================

WEAVIATE_URL = "http://localhost:8080"
HTML_FOLDER = "path/to/html"
GOLDEN_QUESTIONS_FILE = "golden_questions.json"

nltk.download("punkt")
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))
model = SentenceTransformer("all-MiniLM-L6-v2")

# ==============================================================
# STEP 1: CONNECT TO WEAVIATE
# ==============================================================

client = weaviate.Client(WEAVIATE_URL)

def check_weaviate():
    if client.is_ready():
        print("✅ Weaviate is ready!")
    else:
        raise Exception("❌ Weaviate is not running. Start the container and retry.")

check_weaviate()

# ==============================================================
# STEP 2: CREATE WEAVIATE SCHEMA
# ==============================================================

def create_schema():
    schema = {
        "classes": [
            {
                "class": "HTMLDocument",
                "description": "Stores extracted text from HTML pages",
                "vectorizer": "text2vec-openai",
                "properties": [
                    {"name": "title", "dataType": ["text"]},
                    {"name": "text", "dataType": ["text"]},
                    {"name": "source", "dataType": ["text"]},
                ]
            }
        ]
    }

    client.schema.delete_all()  # Clear previous schema if exists
    client.schema.create(schema)
    print("✅ Weaviate schema created successfully.")

create_schema()

# ==============================================================
# STEP 3: EXTRACT FAQ DATA FROM HTML
# ==============================================================

def extract_text_from_html(html_path):
    with open(html_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    title = soup.title.string if soup.title else "Untitled"
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    headers = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]

    return {
        "title": title,
        "text": " ".join(paragraphs),
        "source": os.path.basename(html_path)
    }

def load_html_data():
    html_texts = []
    for filename in os.listdir(HTML_FOLDER):
        if filename.endswith(".html"):
            html_path = os.path.join(HTML_FOLDER, filename)
            extracted = extract_text_from_html(html_path)
            html_texts.append(extracted)
    return html_texts

html_data = load_html_data()
print(f"✅ Extracted {len(html_data)} HTML files.")

# ==============================================================
# STEP 4: LOAD DATA INTO WEAVIATE
# ==============================================================

def upload_to_weaviate(html_data):
    for doc in html_data:
        client.data_object.create(
            data_object={
                "title": doc["title"],
                "text": doc["text"],
                "source": doc["source"]
            },
            class_name="HTMLDocument"
        )
        time.sleep(0.1)  # Avoid rate limits
    print("✅ HTML data uploaded to Weaviate.")

upload_to_weaviate(html_data)

# ==============================================================
# STEP 5: QUERY WEAVIATE FOR GOLDEN QUESTIONS
# ==============================================================

def query_weaviate(question):
    response = client.query.get("HTMLDocument", ["title", "text", "source"]) \
        .with_near_text({"concepts": [question]}) \
        .with_limit(3) \
        .do()
    
    return response["data"]["Get"]["HTMLDocument"]

# ==============================================================
# STEP 6: LOAD GOLDEN QUESTIONS
# ==============================================================

with open(GOLDEN_QUESTIONS_FILE, "r") as f:
    golden_questions = json.load(f)

print(f"✅ Loaded {len(golden_questions)} golden questions.")

# ==============================================================
# STEP 7: COMPUTE F1 SCORE
# ==============================================================

def compute_f1(pred_answer, expected_answer):
    pred_embedding = model.encode(pred_answer, convert_to_tensor=True)
    exp_embedding = model.encode(expected_answer, convert_to_tensor=True)
    return util.pytorch_cos_sim(pred_embedding, exp_embedding).item()

def evaluate_f1_score():
    f1_scores = []
    for q in golden_questions:
        retrieved_results = query_weaviate(q["question"])
        best_result = retrieved_results[0]["text"] if retrieved_results else ""
        f1 = compute_f1(best_result, q["expected_answer"])
        f1_scores.append(f1)

    average_f1 = sum(f1_scores) / len(f1_scores)
    print(f"📊 Average F1 Score: {average_f1:.3f}")

evaluate_f1_score()

# ==============================================================
# CLEANUP AND CLOSE
# ==============================================================

print("✅ Completed Weaviate FAQ ingestion and F1 evaluation.")
