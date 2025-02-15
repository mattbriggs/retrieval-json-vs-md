import json
import os
import nltk
import time
from neo4j import GraphDatabase
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer, util

# 🔹 Configure Neo4J connection
NEO4J_URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "password"

# 🔹 Setup NLP
nltk.download("punkt")
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))
model = SentenceTransformer("all-MiniLM-L6-v2")

# 🔹 Connect to Neo4J
driver = GraphDatabase.driver(NEO4J_URI, auth=(USERNAME, PASSWORD))

def run_query(query, params=None):
    with driver.session() as session:
        return session.run(query, params)

# ==============================================================
# STEP 1: LOAD JSON-LD FILES
# ==============================================================

def load_jsonld_from_folder(folder_path):
    jsonld_data = []
    for file in os.listdir(folder_path):
        if file.endswith(".jsonld"):
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                jsonld_data.append(data)
    return jsonld_data

def extract_faq_entries(jsonld_data):
    faqs = []
    for doc in jsonld_data:
        if "@type" in doc and doc["@type"] == "FAQPage":
            for qa in doc.get("mainEntity", []):
                question = qa.get("name", "").strip()
                answer = qa.get("acceptedAnswer", {}).get("text", "").strip()
                if question and answer:
                    faqs.append({"id": len(faqs) + 1, "question": question, "answer": answer})
    return faqs

# ==============================================================
# STEP 2: CREATE GRAPH SCHEMA
# ==============================================================

def create_schema():
    query = """
    CREATE CONSTRAINT IF NOT EXISTS ON (c:Content) ASSERT c.id IS UNIQUE;
    CREATE CONSTRAINT IF NOT EXISTS ON (t:Term) ASSERT t.name IS UNIQUE;
    CREATE CONSTRAINT IF NOT EXISTS ON (cn:Concept) ASSERT cn.name IS UNIQUE;
    CREATE CONSTRAINT IF NOT EXISTS ON (sc:SuperCategory) ASSERT sc.name IS UNIQUE;
    """
    run_query(query)
    print("✅ Schema constraints created.")

# ==============================================================
# STEP 3: LOAD DATA INTO NEO4J
# ==============================================================

def load_faq_into_neo4j(faq_entries):
    query = """
    UNWIND $faq_entries AS faq
    MERGE (c:Content {id: faq.id})
    SET c.question = faq.question, c.answer = faq.answer
    """
    run_query(query, {"faq_entries": faq_entries})
    print(f"✅ Loaded {len(faq_entries)} FAQ entries into Neo4J.")

def extract_terms(text):
    words = word_tokenize(text.lower())
    return [w for w in words if w.isalnum() and w not in stop_words]

def load_terms():
    query = """
    MATCH (c:Content)
    UNWIND split(c.question, ' ') AS term
    WITH DISTINCT term WHERE term <> ''
    MERGE (t:Term {name: term})
    MERGE (c)-[:RELATED_TO]->(t)
    """
    run_query(query)
    print("✅ Extracted and linked terms to Content.")

# ==============================================================
# STEP 4: ANSWER QUESTIONS WITH CYPHER
# ==============================================================

def query_neo4j(question):
    query = """
    MATCH (c:Content)
    WHERE toLower(c.question) CONTAINS toLower($question)
    RETURN c.answer LIMIT 3
    """
    result = run_query(query, {"question": question})
    return [record["c.answer"] for record in result]

# ==============================================================
# STEP 5: COMPUTE F1 SCORE
# ==============================================================

def compute_f1(pred_answer, expected_answer):
    pred_embedding = model.encode(pred_answer, convert_to_tensor=True)
    exp_embedding = model.encode(expected_answer, convert_to_tensor=True)
    return util.pytorch_cos_sim(pred_embedding, exp_embedding).item()

def evaluate_f1_score(golden_questions):
    f1_scores = []
    for q in golden_questions:
        retrieved = query_neo4j(q["question"])
        best_answer = retrieved[0] if retrieved else ""
        f1 = compute_f1(best_answer, q["expected_answer"])
        f1_scores.append(f1)

    avg_f1 = sum(f1_scores) / len(f1_scores)
    print(f"📊 Average F1 Score: {avg_f1:.3f}")

# ==============================================================
# MAIN EXECUTION
# ==============================================================

def main():
    jsonld_folder = "path/to/jsonld"
    golden_questions_file = "golden_questions.json"

    # 🔹 Load JSON-LD FAQ data
    jsonld_data = load_jsonld_from_folder(jsonld_folder)
    faq_entries = extract_faq_entries(jsonld_data)

    # 🔹 Load golden question set
    with open(golden_questions_file, "r") as f:
        golden_questions = json.load(f)

    # 🔹 Create Graph Schema
    create_schema()

    # 🔹 Load Data into Neo4J
    load_faq_into_neo4j(faq_entries)
    time.sleep(2)
    load_terms()

    # 🔹 Evaluate F1 Score
    evaluate_f1_score(golden_questions)

if __name__ == "__main__":
    main()
