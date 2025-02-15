# **📋 Instructions to Run the Script**
1. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

2. **Ensure Weaviate is Running in Docker**
   ```sh
   docker run -d --rm --name weaviate -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
       -e PERSISTENCE_DATA_PATH=/var/lib/weaviate -e QUERY_DEFAULTS_LIMIT=25 \
       -e ENABLE_MODULES=text2vec-openai -e OPENAI_APIKEY=<your-openai-key> \
       -p 8080:8080 semitechnologies/weaviate:1.22.1
   ```
   Replace `<your-openai-key>` with your OpenAI API key.

3. **Prepare Data**
   - Place **HTML files** in `path/to/html/`
   - Create `golden_questions.json` in the format:
     ```json
     [
       {"question": "What is AI?", "expected_answer": "AI stands for artificial intelligence..."}
     ]
     ```

4. **Run the Script**
   ```sh
   python html_load_faq_weaviate.py
   ```

---

## **📌 What This Script Does**
✅ **Extracts text from HTML FAQ pages**  
✅ **Creates Weaviate schema**  
✅ **Loads HTML FAQ data into Weaviate**  
✅ **Executes semantic search queries**  
✅ **Compares retrieved answers with golden dataset**  
✅ **Computes and prints F1 Score**  

---

### **🔹 Next Steps**
- **Improve Matching**: Use hybrid search (keyword + vector similarity).
- **Expand Evaluation**: Use **BLEU, ROUGE, or METEOR** for more refined scoring.
- **Integrate with Neo4J**: Cross-check results with **structured JSON-LD data**.

🚀 **This script fully automates FAQ ingestion, retrieval, and evaluation using Weaviate!** Let me know if you need adjustments!