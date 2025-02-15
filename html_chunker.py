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
