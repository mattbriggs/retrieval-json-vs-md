import os
import json
import weaviate
import weaviate.classes.config as wc
import nltk
import textwrap
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer, util

# ==============================================================
# CONFIGURATION
# ==============================================================

WEAVIATE_URL = "http://localhost:8080"  # Adjust if running remotely
HTML_FOLDER = "/Users/mattbriggs/Data/retrievaldata/HTML"
GOLDEN_QUESTIONS_FILE = "golden_questions.json"
OUTPUT_F1_JSON = "HTML_F1_result.json"

MAX_TOKENS = 8000  # To avoid exceeding OpenAI token limits

# OpenAI API Key (Ensure this is set in the environment)
OPENAI_API_KEY = os.getenv("OPENAI_APIKEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OpenAI API Key is missing! Set OPENAI_APIKEY in environment.")

nltk.download("punkt")
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))
model = SentenceTransformer("all-MiniLM-L6-v2")

# ==============================================================
# STEP 1: CONNECT TO WEAVIATE
# ==============================================================
client = weaviate.connect_to_local(headers={"X-OpenAI-Api-Key": OPENAI_API_KEY})

def check_weaviate():
    if client.is_ready():
        print("✅ Weaviate is ready!")
    else:
        raise Exception("❌ Weaviate is not running. Start the container and retry.")

check_weaviate()

# ==============================================================
# STEP 2: CREATE WEAVIATE COLLECTION
# ==============================================================

def create_collection():
    """Creates the Weaviate collection if it doesn't exist."""
    collection_name = "HTMLDocument"

    # Get existing collection names as a list of strings
    existing_collections = client.collections.list_all()

    if collection_name in existing_collections:
        print(f"✅ Collection '{collection_name}' already exists.")
        return client.collections.get(collection_name)

    # Create collection
    print(f"🚀 Creating collection '{collection_name}'...")
    collection = client.collections.create(
        name=collection_name,
        properties=[
            wc.Property(name="title", data_type=wc.DataType.TEXT),
            wc.Property(name="text", data_type=wc.DataType.TEXT),
            wc.Property(name="source", data_type=wc.DataType.TEXT),
        ],
        vectorizer_config=wc.Configure.Vectorizer.text2vec_openai(),
        generative_config=wc.Configure.Generative.openai()
    )

    print("✅ Weaviate collection created successfully.")
    return collection

# Ensure collection exists
collection = create_collection()

# ==============================================================
# STEP 3: EXTRACT FAQ DATA FROM HTML
# ==============================================================

def truncate_text(text, max_tokens=MAX_TOKENS):
    """Truncates text to avoid OpenAI's max token limit."""
    words = text.split()
    if len(words) > max_tokens:
        return " ".join(words[:max_tokens]) + "..."
    return text

def extract_text_from_html(html_path):
    """Extracts title, text, and source from an HTML page."""
    with open(html_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    title = soup.title.string if soup.title else "Untitled"
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    headers = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]

    return {
        "title": title,
        "text": truncate_text(" ".join(paragraphs + headers)),
        "source": os.path.basename(html_path)
    }

def load_html_data():
    """Loads all HTML documents from the specified folder."""
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


def chunk_text(text, max_tokens=8000):
    """Splits long text into smaller chunks to fit within OpenAI's context limit."""
    return textwrap.wrap(text, width=max_tokens)

def upload_to_weaviate(html_data):
    """Uploads extracted FAQ data to Weaviate, ensuring text is within token limits."""
    collection = client.collections.get("HTMLDocument")

    for doc in html_data:
        text_chunks = chunk_text(doc["text"])  # Ensure the text is within limits

        for chunk in text_chunks:
            data_object = {
                "title": doc["title"],
                "text": chunk,  # Store the chunked text
                "source": doc["source"]
            }

            try:
                collection.data.insert(data_object)
                print(f"✅ Inserted document '{doc['title']}' successfully.")
            except Exception as e:
                print(f"❌ Error inserting document '{doc['title']}': {e}")

    print("✅ All documents uploaded to Weaviate.")

# ==============================================================
# STEP 5: QUERY WEAVIATE FOR GOLDEN QUESTIONS
# ==============================================================

def query_weaviate(question):
    """Queries Weaviate for the best matching answer to a question."""
    collection = client.collections.get("HTMLDocument")  # Retrieve the correct collection

    response = collection.query.near_text(question, limit=1)  # Remove `.do()`

    # Extract the most relevant result if available
    result = response.objects  # Use `.objects` to get the data
    if result:
        return result[0].properties.get("text", "")  # Extract the best matching text
    return ""

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
    """Computes the F1-score based on cosine similarity."""
    pred_embedding = model.encode(pred_answer, convert_to_tensor=True)
    exp_embedding = model.encode(expected_answer, convert_to_tensor=True)
    return util.pytorch_cos_sim(pred_embedding, exp_embedding).item()

def evaluate_f1_score():
    """Evaluates the F1 score for Weaviate retrieval performance."""
    results = []
    f1_scores = []

    for q in golden_questions:
        retrieved_answer = query_weaviate(q["question"])
        f1 = compute_f1(retrieved_answer, q["expected_answer"])
        f1_scores.append(f1)

        results.append({
            "question": q["question"],
            "expected_answer": q["expected_answer"],
            "retrieved_answer": retrieved_answer,
            "f1_score": f1
        })

    average_f1 = sum(f1_scores) / len(f1_scores)
    print(f"📊 Average F1 Score: {average_f1:.3f}")

    # Save detailed results to JSON
    with open(OUTPUT_F1_JSON, "w") as f:
        json.dump({"average_f1": average_f1, "results": results}, f, indent=4)

    print(f"✅ F1 scores saved to {OUTPUT_F1_JSON}")

evaluate_f1_score()

# ==============================================================
# CLEANUP AND CLOSE
# ==============================================================
client.close()
print("✅ Completed Weaviate FAQ ingestion and F1 evaluation.")