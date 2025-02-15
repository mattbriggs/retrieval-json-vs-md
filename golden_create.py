import os
import json
import nltk
from bs4 import BeautifulSoup

# 🔹 Configure paths
JSONLD_FOLDER = "path/to/jsonld"
HTML_FOLDER = "path/to/html"
OUTPUT_FILE = "golden_questions.json"

# 🔹 Setup NLTK (for basic text cleaning)
nltk.download("punkt")

# ==============================================================
# STEP 1: EXTRACT FAQ DATA FROM JSON-LD
# ==============================================================

def extract_faq_from_jsonld(jsonld_folder):
    """Extract questions and answers from JSON-LD FAQPage schemas."""
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

    print(f"✅ Extracted {len(golden_data)} questions from JSON-LD.")
    return golden_data

# ==============================================================
# STEP 2: EXTRACT FAQ DATA FROM HTML
# ==============================================================

def extract_faq_from_html(html_folder):
    """Extract questions and answers from HTML FAQ sections."""
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

    print(f"✅ Extracted {len(golden_data)} questions from HTML.")
    return golden_data

# ==============================================================
# STEP 3: MERGE AND DEDUPLICATE DATA
# ==============================================================

def merge_and_deduplicate(jsonld_questions, html_questions):
    """Merge questions from JSON-LD and HTML, removing duplicates."""
    merged = {q["question"]: q["expected_answer"] for q in jsonld_questions}  # JSON-LD baseline
    for q in html_questions:
        merged[q["question"]] = q["expected_answer"]  # HTML version may have slight differences

    final_golden_questions = [{"question": q, "expected_answer": a} for q, a in merged.items()]
    print(f"✅ Merged and deduplicated: {len(final_golden_questions)} final golden questions.")
    return final_golden_questions

# ==============================================================
# MAIN EXECUTION
# ==============================================================

def main():
    # 🔹 Extract FAQ questions & answers
    jsonld_questions = extract_faq_from_jsonld(JSONLD_FOLDER)
    html_questions = extract_faq_from_html(HTML_FOLDER)

    # 🔹 Merge & Deduplicate
    golden_questions = merge_and_deduplicate(jsonld_questions, html_questions)

    # 🔹 Save to JSON
    with open(OUTPUT_FILE, "w") as f:
        json.dump(golden_questions, f, indent=4)

    print(f"✅ Golden dataset saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
