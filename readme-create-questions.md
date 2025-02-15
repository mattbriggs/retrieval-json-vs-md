### **📜 Procedure for Creating the Golden Data Set of Questions**
This procedure outlines how to **extract, validate, and format** a **golden dataset of questions and expected answers** from a common content source that has both **HTML and JSON-LD versions**. The resulting dataset will be compatible with **both the Weaviate (HTML) and Neo4J (JSON-LD) scripts**.

---

## **📌 Step 1: Define the Purpose of the Golden Data Set**
The golden dataset is a **benchmark set of questions** with **expected answers** that will be used to measure the **retrieval effectiveness** of:
- **Semantic search in Weaviate (HTML content)**
- **Graph-based structured search in Neo4J (JSON-LD content)**

Each question should:
✅ Be **clear and unambiguous**  
✅ Cover **various content sections** (FAQs, headers, structured information)  
✅ Include **expected answers** that are present in **both HTML and JSON-LD**

---

## **📌 Step 2: Extract Questions from JSON-LD and HTML**
We will extract **FAQ-style questions** and **answers** from both **HTML** and **JSON-LD FAQPage** versions of the content.

### **2.1 Parse JSON-LD to Extract FAQs**
Run this script to extract **questions and answers** from JSON-LD files:
```python
import json
import os

def extract_faq_from_jsonld(jsonld_folder):
    golden_data = []
    
    for file in os.listdir(jsonld_folder):
        if file.endswith(".jsonld"):
            with open(os.path.join(jsonld_folder, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                
                if "@type" in data and data["@type"] == "FAQPage":
                    for qa in data.get("mainEntity", []):
                        question = qa.get("name", "").strip()
                        answer = qa.get("acceptedAnswer", {}).get("text", "").strip()
                        if question and answer:
                            golden_data.append({"question": question, "expected_answer": answer})

    return golden_data

jsonld_folder = "path/to/jsonld"
golden_questions_jsonld = extract_faq_from_jsonld(jsonld_folder)

with open("golden_questions.json", "w") as f:
    json.dump(golden_questions_jsonld, f, indent=4)

print(f"✅ Extracted {len(golden_questions_jsonld)} questions from JSON-LD.")
```

---

### **2.2 Extract Questions from HTML FAQs**
Run this script to extract **questions and answers** from HTML:
```python
from bs4 import BeautifulSoup

def extract_faq_from_html(html_folder):
    golden_data = []

    for file in os.listdir(html_folder):
        if file.endswith(".html"):
            with open(os.path.join(html_folder, file), "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

                faq_sections = soup.find_all("section", {"class": "faq"})
                for section in faq_sections:
                    for q in section.find_all("h2"):  # Assuming questions are in <h2> tags
                        answer = q.find_next_sibling("p")  # Assuming answer is the next paragraph
                        if q and answer:
                            golden_data.append({"question": q.get_text(strip=True), "expected_answer": answer.get_text(strip=True)})

    return golden_data

html_folder = "path/to/html"
golden_questions_html = extract_faq_from_html(html_folder)

with open("golden_questions.json", "w") as f:
    json.dump(golden_questions_html, f, indent=4)

print(f"✅ Extracted {len(golden_questions_html)} questions from HTML.")
```

---

## **📌 Step 3: Merge and Deduplicate Questions**
Since **JSON-LD and HTML FAQs** originate from the same content, we need to **merge** the extracted datasets and remove duplicate questions.

```python
def merge_and_deduplicate(jsonld_questions, html_questions):
    merged = {q["question"]: q["expected_answer"] for q in jsonld_questions}  # JSON-LD baseline
    for q in html_questions:
        merged[q["question"]] = q["expected_answer"]  # HTML version may have slight differences
    
    return [{"question": q, "expected_answer": a} for q, a in merged.items()]

golden_questions = merge_and_deduplicate(golden_questions_jsonld, golden_questions_html)

with open("golden_questions.json", "w") as f:
    json.dump(golden_questions, f, indent=4)

print(f"✅ Merged and deduplicated: {len(golden_questions)} final golden questions.")
```

---

## **📌 Step 4: Validate the Golden Dataset**
Now that we have a cleaned dataset, we need to **ensure quality and consistency**.

### **4.1 Check for Missing or Duplicate Entries**
```python
for q in golden_questions:
    if not q["question"] or not q["expected_answer"]:
        print(f"❌ Warning: Missing data in question: {q['question']}")
```

### **4.2 Ensure JSON Format is Correct**
Manually inspect `golden_questions.json` to verify it looks like this:
```json
[
    {
        "question": "What is machine learning?",
        "expected_answer": "Machine learning is a subset of artificial intelligence that enables computers to learn patterns from data."
    },
    {
        "question": "How does artificial intelligence work?",
        "expected_answer": "Artificial intelligence works by using algorithms to process and analyze data, often leveraging machine learning techniques."
    }
]
```

---

## **📌 Step 5: Use the Golden Dataset for Evaluation**
Now that we have a validated `golden_questions.json`, it can be used by **both Weaviate (HTML) and Neo4J (JSON-LD) scripts**.

### **To test in Weaviate:**
```sh
python html_load_faq_weaviate.py
```

### **To test in Neo4J:**
```sh
python load_faq_neo4j.py
```

Each script will:
✅ Load the golden dataset  
✅ Retrieve answers from **Weaviate (HTML)** or **Neo4J (JSON-LD)**  
✅ Compute **F1 Score** for retrieval accuracy  

---

## **📌 Summary of Steps**
| **Step** | **Action** |
|----------|------------|
| **1** | Extract **questions and answers** from **JSON-LD** |
| **2** | Extract **questions and answers** from **HTML** |
| **3** | **Merge & deduplicate** JSON-LD & HTML data |
| **4** | **Validate** dataset (check for missing/duplicate entries) |
| **5** | Save dataset as `golden_questions.json` |
| **6** | **Use dataset** in Weaviate & Neo4J evaluation scripts |

---

## **📌 Next Steps**
🔹 **Expand the dataset**: Add more questions from **structured metadata**  
🔹 **Use embeddings**: Compare expected answers with **pre-trained NLP models**  
🔹 **Fine-tune retrieval**: Optimize Weaviate & Neo4J queries for better recall  

🚀 **With this golden dataset, you now have a reliable benchmark to test structured vs. unstructured information retrieval!** Let me know if you need refinements! 🎯