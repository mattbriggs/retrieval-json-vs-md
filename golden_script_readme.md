# **📋 Instructions to Run the Script**
1. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

2. **Ensure JSON-LD and HTML Files Are Available**
   - Place **JSON-LD files** in `path/to/jsonld/`
   - Place **HTML files** in `path/to/html/`

3. **Run the Script**
   ```sh
   python generate_golden_questions.py
   ```

4. **Verify the Output**
   - The generated `golden_questions.json` should look like:
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

## **📌 What This Script Does**
✅ **Extracts FAQ questions & answers** from both **JSON-LD & HTML**  
✅ **Merges & deduplicates** questions to remove redundancy  
✅ **Saves the golden dataset** in a **standardized JSON format**  
✅ **Ensures compatibility** with **both Weaviate (HTML) & Neo4J (JSON-LD) evaluation scripts**  

🚀 **This single script simplifies golden dataset creation, making it easy to benchmark structured vs. unstructured retrieval!** Let me know if you need refinements. 🎯