import os
import json
import weaviate
import weaviate.classes.config as wc
import nltk
import textwrap
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer, util
import subprocess

# ==============================================================
# CONFIGURATION
# ==============================================================

WEAVIATE_URL = "http://localhost:8080"  # Adjust if running remotely
GOLDEN_QUESTIONS_FILE = "golden_questions.json"
OUTPUT_F1_JSON = "json_f1_result-vector-related.json"
MAX_TOKENS = 8000  # To avoid exceeding OpenAI token limits

# Download NLTK resources if not already present
nltk.download("punkt")
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

# Load SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# ==============================================================
# STEP 1: CONNECT TO WEAVIATE AND FETCH API KEY
# ==============================================================

def get_openai_api_key(container_name="weaviate"):
    """Retrieve OpenAI API Key from the Weaviate Docker container's environment variables."""
    try:
        result = subprocess.run(
            ["docker", "exec", container_name, "env"],
            capture_output=True,
            text=True,
            check=True,
        )

        for line in result.stdout.split("\n"):
            if "OPENAI_APIKEY=" in line:
                return line.split("=")[1].strip()

        raise ValueError("❌ OpenAI API Key not found in Weaviate container.")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"❌ ERROR: Unable to retrieve API key from container '{container_name}': {e}")

# Fetch the OpenAI API Key from the running Weaviate container
OPENAI_API_KEY = get_openai_api_key()

print(f"✅ Retrieved OpenAI API Key from Weaviate: {OPENAI_API_KEY[:6]}***")  # Masked for security

# Connect to Weaviate with the retrieved API key
client = weaviate.connect_to_local(headers={"X-OpenAI-Api-Key": OPENAI_API_KEY})

def check_weaviate():
    """Check if Weaviate is running and accessible."""
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
    collection_name = "FAQ"

    existing_collections = client.collections.list_all()

    if collection_name in existing_collections:
        print(f"✅ Collection '{collection_name}' already exists.")
        return client.collections.get(collection_name)

    # Create collection
    print(f"🚀 Creating collection '{collection_name}'...")
    collection = client.collections.create(
        name=collection_name,
        properties=[
            wc.Property(name="question", data_type=wc.DataType.TEXT),
            wc.Property(name="answer", data_type=wc.DataType.TEXT),
        ],
        vectorizer_config=wc.Configure.Vectorizer.text2vec_openai(),
        generative_config=wc.Configure.Generative.openai()
    )

    print("✅ Weaviate collection created successfully.")
    return collection

collection = create_collection()

# ==============================================================
# STEP 3: LOAD FAQ DATA INTO WEAVIATE
# ==============================================================

def load_faq_data():
    """Loads FAQ data from JSON and inserts it into Weaviate."""
    with open(GOLDEN_QUESTIONS_FILE, "r") as f:
        faq_data = json.load(f)

    print(f"📥 Loading {len(faq_data)} FAQs into Weaviate...")

    for faq in faq_data:
        data_object = {
            "question": faq["question"],
            "answer": faq["expected_answer"]
        }
        try:
            collection.data.insert(data_object)
            print(f"✅ Inserted: {faq['question']}")
        except Exception as e:
            print(f"❌ Error inserting {faq['question']}: {e}")

    print("✅ All FAQs uploaded to Weaviate.")

load_faq_data()

# ==============================================================
# STEP 4: QUERY WEAVIATE FOR GOLDEN QUESTIONS
# ==============================================================

def query_weaviate(question):
    """Queries Weaviate for the best matching answer to a question."""
    collection = client.collections.get("FAQ")

    try:
        # Corrected syntax: Pass the question string directly
        response = collection.query.near_text(question, limit=1)

        # Extract the most relevant result if available
        result = response.objects if response else []

        if result:
            return result[0].properties.get("answer", "")

    except Exception as e:
        print(f"❌ Query error for '{question}': {e}")

    return ""

# ==============================================================
# STEP 5: COMPUTE F1 SCORE
# ==============================================================

def compute_f1(pred_answer, expected_answer):
    """Computes the F1-score based on cosine similarity."""
    if not pred_answer.strip():
        return 0.0  # Return 0 score if no answer was retrieved

    pred_embedding = model.encode(pred_answer, convert_to_tensor=True)
    exp_embedding = model.encode(expected_answer, convert_to_tensor=True)
    return util.pytorch_cos_sim(pred_embedding, exp_embedding).item()

def evaluate_f1_score():
    """Evaluates the F1 score for Weaviate retrieval performance."""
    results = []
    f1_scores = []

    with open(GOLDEN_QUESTIONS_FILE, "r") as f:
        golden_questions = json.load(f)

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

        print(f"🔍 Q: {q['question']}")
        print(f"✅ Expected: {q['expected_answer']}")
        print(f"📌 Retrieved: {retrieved_answer}")
        print(f"🎯 F1 Score: {f1:.3f}\n")

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