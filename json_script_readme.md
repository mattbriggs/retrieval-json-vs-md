
# **📋 Instructions to Run the Script**
1. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

2. **Ensure Neo4J is Running Locally**
   - Start your local Neo4J instance.
   - Ensure it's available at `bolt://localhost:7687` with user `neo4j` and password `password`.
   - Run `neo4j console` if needed.

3. **Prepare Data**
   - Place JSON-LD files in `path/to/jsonld/`
   - Place golden questions in `golden_questions.json` in the format:
     ```json
     [
       {"question": "What is AI?", "expected_answer": "AI stands for artificial intelligence..."}
     ]
     ```

4. **Run the Script**
   ```sh
   python load_faq_neo4j.py
   ```

---

## **📌 What This Script Does**
✅ **Extracts FAQ data** from JSON-LD files  
✅ **Creates Neo4J graph schema** (Content → Term → Concept)  
✅ **Loads FAQ data into Neo4J**  
✅ **Generates Term nodes and connects them**  
✅ **Answers questions using Cypher queries**  
✅ **Computes F1 Score using sentence similarity**  

---

### **🔹 Next Steps**
- **Expand Graph Taxonomy**: Add **Concept** and **SuperCategory** relationships.
- **Improve Queries**: Use **embedding-based search** instead of simple keyword matching.
- **Hybrid Retrieval**: Combine **vector search** with **graph queries** for more accurate answers.

🚀 **This script fully automates the pipeline from JSON-LD to Neo4J, with evaluation using F1 score.** Let me know if you need refinements!