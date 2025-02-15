# Study Design: Evaluating Structured vs. Unstructured Content for AI Readiness

## **Introduction**
This study examines how different content structures—**structured JSON-LD (Schema.org)** and **unstructured HTML**—impact **AI-driven information retrieval**. The goal is to assess which format enables more **accurate, efficient, and AI-ready** search results, using **F1 score** as the primary evaluation metric.

### **Business Context**
Companies increasingly rely on AI-powered search and recommendation systems to extract insights from large-scale content repositories. Ensuring content is structured in a way that enhances machine understanding can directly impact:
- **Customer self-service efficiency** (e.g., chatbots, FAQ retrieval)
- **Internal knowledge management** (e.g., employee portals, document search)
- **Search engine optimization (SEO)** and structured data compliance

This study aims to provide **data-driven insights** on whether structuring content as **JSON-LD** (used in knowledge graphs) improves information retrieval over **raw HTML** (often used in traditional web search).

---

## **Study Design & Methodology**

### **Content Sources & Formats**
This study evaluates the same content in two different formats:
1. **HTML-based FAQ pages**: Generated from Markdown (MD), representing traditional web content.
2. **JSON-LD structured content**: Derived from YAML, adhering to **Schema.org’s FAQPage** schema, used in knowledge graphs and AI-driven search systems.

### **Evaluation Approach**
The effectiveness of each format is measured by how accurately it answers **golden dataset questions**—a standardized set of business-relevant queries. The study follows these key steps:

### **Step 1: Data Preparation**
- **Extract structured content** from **JSON-LD (Schema.org FAQPage format)**.
- **Extract unstructured content** from **HTML FAQ pages**.
- Normalize the content to create a **golden question dataset**—a set of real-world business queries with predefined correct answers.

### **Step 2: Indexing & AI Retrieval**
- **HTML Search (Weaviate, AI-powered search):**
  - Store **HTML FAQ content** in Weaviate, an AI-driven **vector search** database.
  - Use **semantic search models** to retrieve answers.
- **JSON-LD Search (Neo4J, Knowledge Graph Retrieval):**
  - Store **JSON-LD FAQ content** as a **knowledge graph** in Neo4J.
  - Use **structured Cypher queries** to retrieve answers based on **semantic relationships**.

### **Step 3: Query Execution & Performance Measurement**
- Run **the same set of golden questions** against both Weaviate (HTML) and Neo4J (JSON-LD).
- Measure **retrieval effectiveness** using **F1 score**, which evaluates:
  - **Precision** (how many retrieved answers were correct)
  - **Recall** (how many correct answers were retrieved)

---

## **Technical Implementation Overview**
### **1. Weaviate (Vector Search for HTML)**
- **Why Weaviate?** Weaviate uses **AI-based vector embeddings**, allowing it to retrieve semantically relevant answers even if the exact query words are not present in the content.
- **Implementation Steps:**
  1. Deploy Weaviate in a local Docker container.
  2. Extract text content from HTML FAQ pages.
  3. Store extracted text in Weaviate with OpenAI-powered **semantic embeddings**.
  4. Run AI-driven searches to find relevant answers.

### **2. Neo4J (Graph Search for JSON-LD)**
- **Why Neo4J?** Neo4J enables **relationship-based retrieval**, leveraging **structured data relationships** to return more contextually accurate answers.
- **Implementation Steps:**
  1. Deploy Neo4J on a local machine.
  2. Load JSON-LD structured FAQ data into a knowledge graph.
  3. Create a hierarchical taxonomy:
     - **Content Nodes** (FAQ items)
     - **Term Nodes** (Keywords from FAQ)
     - **Concept Nodes** (High-level categories)
     - **Supercategories** (Broader domains)
  4. Execute **structured Cypher queries** to retrieve answers.

---

## **Expected Business Insights**
This study provides empirical data to help organizations understand:

1. **Does structured JSON-LD data improve AI-powered retrieval?**
   - If JSON-LD (Neo4J) outperforms HTML (Weaviate), it validates that **structured content enhances machine understanding**.
   
2. **How effective is AI-driven vector search for unstructured data?**
   - If Weaviate performs well, businesses may not need full schema compliance for effective AI search.
   
3. **How should businesses structure content for AI-readiness?**
   - The results will help companies **decide on content formatting strategies** for AI-based search, chatbots, and knowledge management systems.

---

## **Conclusion**
This study compares **structured vs. unstructured information retrieval** to determine the best strategy for **AI-powered business search applications**. By applying **F1 score measurement**, businesses can make **data-driven decisions** on how to format content for better AI readiness.

The findings will provide **practical recommendations** on:
✅ Whether structured **JSON-LD knowledge graphs** should be prioritized over traditional **HTML FAQs**.
✅ How **vector search AI** can compensate for **unstructured content**.
✅ Best practices for **optimizing enterprise search** using **graph vs. AI-based retrieval**.

By leveraging these insights, organizations can enhance **customer self-service**, improve **internal knowledge retrieval**, and boost **AI-driven decision-making**.

