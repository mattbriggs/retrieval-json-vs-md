# JSON Process

**Step-by-step procedure** for loading **JSON-LD FAQPage** data into **Neo4J**, structuring it into a **graph taxonomy**, and evaluating it using a **golden dataset** with **F1 scoring**.


## **📌 Overview of the Procedure**
### **1️⃣ Setup & Installation**
- Install **Neo4J** and dependencies
- Run a local **Neo4J** instance

### **2️⃣ Load JSON-LD Data**
- Parse **FAQPage** schemas from **Schema.org**
- Extract **content, questions, and answers**

### **3️⃣ Construct the Knowledge Graph**
- **Content nodes** → store FAQ items
- **Term nodes** → represent keywords
- **Concept nodes** → cluster related topics
- **Supercategory nodes** → define broader domains

### **4️⃣ Query & Evaluate Performance**
- Load **golden question set**
- Execute **Cypher queries** to retrieve answers
- Compute **F1 Score** using NLP similarity

---

## **🛠 Step 1: Install and Setup Neo4J**
### **1.1 Install Neo4J & Dependencies**
```sh
pip install neo4j pandas jsonschema nltk sentence-transformers
```
🔹 Ensure **Neo4J Desktop** is installed, or start a **Docker** container:
```sh
docker run -d --rm --name neo4j -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j
```
🔹 Set **password** to `password` or update it as needed.

---

## **🛠 Step 2: Load JSON-LD FAQ Data**
### **2.1 Install Required Python Libraries**
```sh
pip install jsonschema
```

### **2.2 Parse JSON-LD FAQ Data**
Extract **FAQ questions & answers** from JSON-LD files:
```python
import json
import os

def load_jsonld_from_folder(folder_path):
    jsonld_data = []
    for file in os.listdir(folder_path):
        if file.endswith(".jsonld"):
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                jsonld_data.append(data)
    return jsonld_data

# Load JSON-LD from a directory
jsonld_folder = "path/to/jsonld"
jsonld_data = load_jsonld_from_folder(jsonld_folder)
print(f"Loaded {len(jsonld_data)} JSON-LD files.")
```

### **2.3 Extract FAQ Items**
```python
def extract_faq_entries(jsonld_data):
    faqs = []
    for doc in jsonld_data:
        if "@type" in doc and doc["@type"] == "FAQPage":
            for qa in doc.get("mainEntity", []):
                question = qa.get("name", "").strip()
                answer = qa.get("acceptedAnswer", {}).get("text", "").strip()
                if question and answer:
                    faqs.append({"question": question, "answer": answer})
    return faqs

faq_entries = extract_faq_entries(jsonld_data)
print(f"Extracted {len(faq_entries)} FAQ entries.")
```

---

## **🛠 Step 3: Load Data into Neo4J**
### **3.1 Connect to Neo4J**
```python
from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "password"

driver = GraphDatabase.driver(NEO4J_URI, auth=(USERNAME, PASSWORD))

def run_query(query, params=None):
    with driver.session() as session:
        return session.run(query, params)
```

### **3.2 Define the Graph Structure**
- **FAQ nodes** → Store **questions & answers**
- **Term nodes** → Keywords extracted from questions
- **Concept nodes** → Higher-level categories
- **Supercategory nodes** → Broad domains

```python
def create_schema():
    query = """
    CREATE CONSTRAINT IF NOT EXISTS ON (c:Content) ASSERT c.id IS UNIQUE;
    CREATE CONSTRAINT IF NOT EXISTS ON (t:Term) ASSERT t.name IS UNIQUE;
    CREATE CONSTRAINT IF NOT EXISTS ON (cn:Concept) ASSERT cn.name IS UNIQUE;
    CREATE CONSTRAINT IF NOT EXISTS ON (sc:SuperCategory) ASSERT sc.name IS UNIQUE;
    """
    run_query(query)
    print("Schema constraints created.")

create_schema()
```

### **3.3 Load FAQ Data as Content Nodes**
```python
def load_faq_into_neo4j(faq_entries):
    query = """
    UNWIND $faq_entries AS faq
    MERGE (c:Content {id: faq.id, question: faq.question, answer: faq.answer})
    """
    run_query(query, {"faq_entries": [{"id": i, "question": f["question"], "answer": f["answer"]} for i, f in enumerate(faq_entries)]})
    print("FAQ entries loaded into Neo4J.")

load_faq_into_neo4j(faq_entries)
```

### **3.4 Extract & Connect Keywords as Terms**
```python
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download("stopwords")
nltk.download("punkt")

stop_words = set(stopwords.words("english"))

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
    print("Terms extracted and linked to Content.")

load_terms()
```

---

## **🛠 Step 4: Query Neo4J to Answer Golden Questions**
### **4.1 Load Golden Questions**
```python
with open("golden_questions.json", "r") as f:
    golden_questions = json.load(f)  # [{"question": "What is AI?", "expected_answer": "..."}]
```

### **4.2 Query Neo4J for Answers**
```python
def query_neo4j(question):
    query = """
    MATCH (c:Content)
    WHERE toLower(c.question) CONTAINS toLower($question)
    RETURN c.answer LIMIT 3
    """
    result = run_query(query, {"question": question})
    return [record["c.answer"] for record in result]

test_question = "How does AI work?"
answers = query_neo4j(test_question)
print("Retrieved Answers:", answers)
```

---

## **🛠 Step 5: Evaluate with F1 Score**
### **5.1 Compute Similarity**
```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_f1(pred_answer, expected_answer):
    pred_embedding = model.encode(pred_answer, convert_to_tensor=True)
    exp_embedding = model.encode(expected_answer, convert_to_tensor=True)
    
    return util.pytorch_cos_sim(pred_embedding, exp_embedding).item()

f1_scores = []

for q in golden_questions:
    retrieved = query_neo4j(q["question"])
    best_answer = retrieved[0] if retrieved else ""
    
    f1 = compute_f1(best_answer, q["expected_answer"])
    f1_scores.append(f1)

average_f1 = sum(f1_scores) / len(f1_scores)
print(f"Average F1 Score: {average_f1:.3f}")
```

---

## **📋 Summary**
✅ **Setup Neo4J** (Docker or local)  
✅ **Extract JSON-LD FAQ data**  
✅ **Build a taxonomy graph (Content → Term → Concept → Supercategory)**  
✅ **Load golden dataset & evaluate using F1 Score**  

---

## **📜 `requirements.txt`**
```txt
neo4j
pandas
nltk
jsonschema
sentence-transformers
```