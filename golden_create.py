import os
import json
import nltk
from bs4 import BeautifulSoup

# 🔹 Configure paths
JSONLD_FOLDER = "/Users/mattbriggs/Data/retrievaldata/JSONLD"
HTML_FOLDER = "/Users/mattbriggs/Data/retrievaldata/HTML"
OUTPUT_FILE = "golden_questions.json"

# 🔹 Setup NLTK (for basic text cleaning)
nltk.download("punkt")

# ==============================================================
# STEP 1: EXTRACT FAQ DATA FROM JSON-LD
# ==============================================================

def extract_faq_from_jsonld(jsonld_folder):
    """Extract questions and answers from JSON-LD FAQPage schemas, handling HTML answers."""
    golden_data = []
    
    for file in os.listdir(jsonld_folder):
        if file.endswith(".json"):
            with open(os.path.join(jsonld_folder, file), "r", encoding="utf-8") as f:
                data = json.load(f)

                # Handle if JSON-LD is wrapped in a list
                if isinstance(data, list):
                    data = data[0]  # Extract first object if it's a list

                if "@type" in data and data["@type"] == "FAQPage":
                    for qa in data.get("mainEntity", []):
                        if qa.get("@type") == "Question":
                            question = qa.get("name", "").strip()
                            answer_html = qa.get("acceptedAnswer", {}).get("text", "").strip()
                            
                            # Convert HTML answers to plain text
                            answer_text = BeautifulSoup(answer_html, "html.parser").get_text(separator=" ")

                            if question and answer_text:
                                golden_data.append({"question": question, "expected_answer": answer_text})

    print(f"✅ Extracted {len(golden_data)} questions from JSON-LD.")
    return golden_data

# ==============================================================
# STEP 2: EXTRACT FAQ DATA FROM HTML
# ==============================================================

def extract_faq_from_html(html_folder):
    """Extract questions and answers from HTML FAQ sections, handling nested content properly."""
    golden_data = []

    for file in os.listdir(html_folder):
        if file.endswith(".html"):
            with open(os.path.join(html_folder, file), "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

                # Find the FAQ content container
                faq_section = soup.find("section", id="faq-content-container")
                if faq_section:
                    # Iterate through h3 elements (questions) and extract their answers
                    for question_tag in faq_section.find_all("h3"):
                        question = question_tag.get_text(strip=True)

                        # The answer is typically in the next div with class 'content'
                        answer_div = question_tag.find_next_sibling("div", class_="content")

                        if answer_div:
                            # Extract text while preserving paragraph structure
                            answer_text = ' '.join(p.get_text(strip=True) for p in answer_div.find_all("p"))

                            if question and answer_text:
                                golden_data.append({"question": question, "expected_answer": answer_text})

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
