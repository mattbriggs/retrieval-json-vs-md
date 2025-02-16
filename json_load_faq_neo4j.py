import json
import os
import nltk
import time
from neo4j import GraphDatabase
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer, util
import re
from bs4 import BeautifulSoup

# 🔹 Load Neo4J Credentials from neocred.json
with open("neocred.json", "r") as f:
    creds = json.load(f)

NEO4J_URI = creds["NEO4J_URI"]
USERNAME = creds["USERNAME"]
PASSWORD = creds["PASSWORD"]

# 🔹 Setup NLP
nltk.download("punkt")
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))
model = SentenceTransformer("all-MiniLM-L6-v2")

# 🔹 Connect to Neo4J
driver = GraphDatabase.driver(NEO4J_URI, auth=(USERNAME, PASSWORD))

def run_query(query, params=None):
    """Runs a Cypher query on the Neo4j database."""
    with driver.session() as session:
        result = session.run(query, params or {})
        return result.data()  # Ensures the result is returned before consumption

# ==============================================================
# STEP 1: CLEAR DATABASE BEFORE WRITING NEW DATA
# ==============================================================
def clear_database():
    """Clears all nodes and relationships in the Neo4j database."""
    query = "MATCH (n) DETACH DELETE n;"
    run_query(query)
    print("🗑️ Cleared all nodes and relationships from the database.")

# ==============================================================
# STEP 2: LOAD JSON-LD FILES
# ==============================================================
def load_jsonld_from_folder(folder_path):
    """Loads JSON-LD data from a given folder and prints what it finds."""
    jsonld_data = []
    
    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return jsonld_data

    print(f"📂 Loading JSON-LD files from: {folder_path}")

    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            file_path = os.path.join(folder_path, file)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    jsonld_data.append(data)
                except json.JSONDecodeError:
                    print(f"❌ Error reading JSON: {file_path}")
    
    print(f"✅ Loaded {len(jsonld_data)} JSON-LD files.")
    return jsonld_data

from bs4 import BeautifulSoup
import json

def clean_text(html_text):
    """Removes HTML tags and trims whitespace from text."""
    return BeautifulSoup(html_text, "html.parser").get_text().strip()

def flatten_jsonld(data):
    """
    Recursively flattens lists and extracts valid FAQPage dictionaries.
    Returns a list of FAQPage dictionaries.
    """
    result = []
    if isinstance(data, dict):
        if data.get("@type") == "FAQPage":
            result.append(data)  # Only add valid FAQPage dictionaries
    elif isinstance(data, list):
        for item in data:
            result.extend(flatten_jsonld(item))  # Recursively flatten lists
    return result


def extract_faq_entries(jsonld_data):
    """Extracts FAQ questions and answers from JSON-LD data."""
    
    faqs = []

    # 🔹 Flatten JSON-LD structure to extract all FAQPage dictionaries
    jsonld_pages = flatten_jsonld(jsonld_data)

    if not jsonld_pages:
        print("❌ No valid FAQPages found. Check your JSON structure.")
        return []

    for entry in jsonld_pages:
        if "mainEntity" not in entry or not isinstance(entry["mainEntity"], list):
            print("⚠️ Skipping entry: No 'mainEntity' key or it's not a list.")
            continue

        # 🔹 Iterate over questions in mainEntity
        for qa in entry["mainEntity"]:
            if not isinstance(qa, dict) or qa.get("@type") != "Question":
                print(f"⚠️ Skipping entry: '@type' is not 'Question' - {qa.get('@type', 'Unknown')}")
                continue

            question = qa.get("name", "").strip()
            raw_answer = qa.get("acceptedAnswer", {}).get("text", "").strip()

            # Clean answer text by removing HTML tags
            answer = clean_text(raw_answer)

            if question and answer:
                faqs.append({"id": len(faqs) + 1, "question": question, "answer": answer})
            else:
                print(f"⚠️ Skipping entry: Missing question or answer. Question: {question}, Answer: {answer}")

    print(f"✅ Extracted {len(faqs)} FAQs.")
    
    if not faqs:
        print("❌ No FAQ entries found. Check your JSON structure.")

    return faqs


# ==============================================================
# STEP 3: CREATE GRAPH SCHEMA
# ==============================================================
def create_schema():
    """Creates unique constraints to optimize queries."""
    query = """
    CREATE CONSTRAINT IF NOT EXISTS FOR (c:Content) REQUIRE c.id IS UNIQUE;
    """
    run_query(query)
    print("✅ Schema constraints created.")

# ==============================================================
# STEP 4: LOAD DATA INTO NEO4J
# ==============================================================
def load_faq_into_neo4j(faq_entries):
    """Inserts FAQ data into Neo4j and creates relationships."""
    
    query = """
    UNWIND $faq_entries AS faq
    MERGE (c:Content {id: faq.id})
    SET c.question = faq.question, c.answer = faq.answer
    WITH c, faq  // ✅ Prevents WITH error before UNWIND
    UNWIND split(faq.question, ' ') AS term
    WITH c, term WHERE term <> ''
    MERGE (t:Term {name: toLower(term)})
    MERGE (c)-[:MENTIONS]->(t)
    """
    
    run_query(query, {"faq_entries": faq_entries})
    print(f"✅ Loaded {len(faq_entries)} FAQ entries and created term relationships.")

    # Link similar questions
    link_similar_faqs()

def link_similar_faqs():
    """Creates relationships between similar FAQ questions."""
    query = """
    MATCH (c1:Content), (c2:Content)
    WHERE c1.id < c2.id AND toLower(c1.question) CONTAINS toLower(c2.question)
    MERGE (c1)-[:RELATED_TO]->(c2)
    """
    run_query(query)
    print("✅ Created relationships between similar FAQ entries.")

# ==============================================================
# STEP 5: ANSWER QUESTIONS WITH CYPHER
# ==============================================================
def query_neo4j(question):
    """Queries Neo4j for the most relevant FAQ answer."""
    query = """
    MATCH (c:Content)
    WHERE toLower(c.question) CONTAINS toLower($question)
    RETURN c.answer AS answer
    LIMIT 3
    """
    result = run_query(query, {"question": question})
    return [record["answer"] for record in result]

# ==============================================================
# STEP 6: COMPUTE F1 SCORE
# ==============================================================
def compute_f1(pred_answer, expected_answer):
    """Computes the F1 similarity score using sentence embeddings."""
    if not pred_answer:
        return 0.0
    pred_embedding = model.encode(pred_answer, convert_to_tensor=True)
    exp_embedding = model.encode(expected_answer, convert_to_tensor=True)
    return util.pytorch_cos_sim(pred_embedding, exp_embedding).item()

def evaluate_f1_score(golden_questions):
    """Evaluates F1 score for each golden question and saves results to a JSON file."""
    f1_results = []
    for q in golden_questions:
        retrieved = query_neo4j(q["question"])
        best_answer = retrieved[0] if retrieved else ""
        f1 = compute_f1(best_answer, q["expected_answer"])
        f1_results.append({"question": q["question"], "expected": q["expected_answer"], "retrieved": best_answer, "f1_score": f1})

    avg_f1 = sum(r["f1_score"] for r in f1_results) / len(f1_results) if f1_results else 0.0
    results = {"average_f1": avg_f1, "detailed_results": f1_results}

    with open("json_f1_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"📊 Average F1 Score: {avg_f1:.3f}")
    print("✅ Results saved to json_f1_result.json")

# ==============================================================
# MAIN EXECUTION
# ==============================================================
def main():
    jsonld_folder = "/Users/mattbriggs/Data/retrievaldata/JSONLD"
    golden_questions_file = "golden_questions.json"

    # 🔹 Load JSON-LD FAQ data
    jsonld_data = load_jsonld_from_folder(jsonld_folder)
    faq_entries = extract_faq_entries(jsonld_data)

    # 🔹 Load golden question set
    with open(golden_questions_file, "r") as f:
        golden_questions = json.load(f)

    # 🔹 Clear Database Before Writing
    clear_database()

    # 🔹 Create Graph Schema
    create_schema()

    # 🔹 Load Data into Neo4J
    load_faq_into_neo4j(faq_entries)
    time.sleep(2)

    # 🔹 Evaluate F1 Score and Save Results
    evaluate_f1_score(golden_questions)

if __name__ == "__main__":
    main()
