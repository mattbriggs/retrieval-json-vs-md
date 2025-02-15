# HTML Study Design using Weaviate

A structured, step-by-step **procedural guide** to setting up **Weaviate** to search an HTML folder and evaluate it against a **golden question dataset**.

---

## **Step 1: Install and Set Up Weaviate**
You can run Weaviate **locally** via Docker or use a **cloud-hosted version**.

### **1.1 Install Docker (if not already installed)**
```sh
sudo apt update && sudo apt install -y docker.io
```
or on macOS:
```sh
brew install --cask docker
```

### **1.2 Run Weaviate via Docker**
```sh
docker run -d --rm --name weaviate -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true -e PERSISTENCE_DATA_PATH=/var/lib/weaviate -e QUERY_DEFAULTS_LIMIT=25 -e ENABLE_MODULES=text2vec-openai -e OPENAI_APIKEY=<your-openai-key> -p 8080:8080 semitechnologies/weaviate:1.22.1
```
- The `ENABLE_MODULES=text2vec-openai` flag enables **OpenAI embeddings** for semantic search.
- Replace `<your-openai-key>` with your OpenAI API key.

---

## **Step 2: Preprocess HTML Files**
We need to extract meaningful text **chunks** from the HTML before storing them in Weaviate.

### **2.1 Install Required Python Libraries**
```sh
pip install beautifulsoup4 weaviate-client openai markdownify
```

### **2.2 Extract Text from HTML**
Use `BeautifulSoup` to extract **meaningful content** (titles, paragraphs, sections).
```python
from bs4 import BeautifulSoup
import os
import json

def extract_text_from_html(html_path):
    with open(html_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    # Extract title, headers, and paragraphs
    title = soup.title.string if soup.title else "Untitled"
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    headers = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]

    # Combine extracted content into a structured dict
    return {
        "title": title,
        "headers": headers,
        "text": " ".join(paragraphs)
    }

# Example usage
html_folder = "path/to/html/folder"
html_texts = []
for filename in os.listdir(html_folder):
    if filename.endswith(".html"):
        html_path = os.path.join(html_folder, filename)
        extracted = extract_text_from_html(html_path)
        extracted["source"] = filename  # Keep track of source file
        html_texts.append(extracted)

# Save extracted content for debugging
with open("html_extracted.json", "w") as f:
    json.dump(html_texts, f, indent=4)
```

---

## **Step 3: Load Extracted Content into Weaviate**
### **3.1 Connect to Weaviate**
```python
import weaviate

client = weaviate.Client("http://localhost:8080")

# Check if Weaviate is running
if client.is_ready():
    print("Weaviate is ready!")
else:
    raise Exception("Weaviate is not running.")
```

### **3.2 Define a Weaviate Schema**
We need to **define a collection (class)** to store the HTML content.
```python
schema = {
    "classes": [
        {
            "class": "HTMLDocument",
            "description": "Stores extracted text from HTML pages",
            "vectorizer": "text2vec-openai",  # Uses OpenAI embeddings
            "properties": [
                {
                    "name": "title",
                    "dataType": ["text"],
                },
                {
                    "name": "headers",
                    "dataType": ["text[]"],  # List of headers
                },
                {
                    "name": "text",
                    "dataType": ["text"],
                },
                {
                    "name": "source",
                    "dataType": ["text"],  # Filename for reference
                },
            ]
        }
    ]
}

# Apply schema
client.schema.delete_all()  # Clear existing schema if needed
client.schema.create(schema)
print("Schema created successfully!")
```

### **3.3 Upload Data to Weaviate**
```python
import time

html_collection = client.data_object

for doc in html_texts:
    html_collection.create(
        data_object={
            "title": doc["title"],
            "headers": doc["headers"],
            "text": doc["text"],
            "source": doc["source"]
        },
        class_name="HTMLDocument"
    )
    time.sleep(0.1)  # To avoid rate limits
print("Documents uploaded successfully!")
```

---

## **Step 4: Query Weaviate with Golden Questions**
### **4.1 Load Golden Question Set**
```python
import json

with open("golden_questions.json", "r") as f:
    golden_questions = json.load(f)  # Format: [{"question": "What is AI?", "expected_answer": "..."}]
```

### **4.2 Perform a Semantic Search in Weaviate**
```python
def query_weaviate(question):
    response = client.query.get("HTMLDocument", ["title", "text", "source"]) \
        .with_near_text({"concepts": [question]}) \
        .with_limit(3) \
        .do()
    
    return response["data"]["Get"]["HTMLDocument"]

# Example Query
test_question = "How does machine learning work?"
results = query_weaviate(test_question)

for res in results:
    print(f"Title: {res['title']}\nText: {res['text'][:300]}...\nSource: {res['source']}\n")
```

---

## **Step 5: Evaluate F1 Score**
### **5.1 Compute Precision, Recall, and F1**
Compare the retrieved text against expected answers using NLP-based similarity (e.g., **TF-IDF, BERT, or ROUGE**).

```python
from sklearn.metrics import f1_score
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def compute_f1(predicted_text, expected_answer):
    pred_embedding = model.encode(predicted_text, convert_to_tensor=True)
    exp_embedding = model.encode(expected_answer, convert_to_tensor=True)
    
    similarity = util.pytorch_cos_sim(pred_embedding, exp_embedding).item()
    return similarity

f1_scores = []

for q in golden_questions:
    retrieved_results = query_weaviate(q["question"])
    best_result = retrieved_results[0]["text"] if retrieved_results else ""

    f1 = compute_f1(best_result, q["expected_answer"])
    f1_scores.append(f1)

average_f1 = sum(f1_scores) / len(f1_scores)
print(f"Average F1 Score: {average_f1:.3f}")
```

---

## **Summary of Steps**
### **1. Setup Weaviate**
- Install & run Weaviate (via Docker)
- Install Python dependencies

### **2. Preprocess HTML**
- Extract meaningful text (titles, headers, body)
- Save extracted data for indexing

### **3. Load Data into Weaviate**
- Define a **schema**
- Upload extracted text to Weaviate

### **4. Query Weaviate**
- Load **golden questions**
- Perform **semantic search** on indexed documents

### **5. Evaluate Performance**
- Compare retrieved answers with **golden answers**
- Compute **F1 Score** using **BERT-based similarity**

---

### **Next Steps**
✅ **Fine-tune embeddings**: Try other vector models (e.g., `text-embedding-ada-002` from OpenAI).  
✅ **Hybrid search**: Combine keyword search with vector search.  
✅ **Expand evaluation**: Use **BLEU, ROUGE, or METEOR** for better text similarity scoring.  

This setup will **fully test how well Weaviate performs against a structured format like JSON-LD in answering golden questions**. 🚀