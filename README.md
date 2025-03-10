# Prepare, set-up, and run two vector search pipelines to compare HTML vs JSON-LD

## Introduction

This study examines how different content structures—**structured JSON-LD (Schema.org)** and **unstructured HTML**—impact **AI-driven information retrieval**. The goal is to assess which format enables more **accurate, efficient, and AI-ready** search results, using **F1 score** as the primary evaluation metric.

### Business Context

Companies increasingly rely on AI-powered search and recommendation systems to extract insights from large-scale content repositories. Ensuring content is structured in a way that enhances machine understanding can directly impact:
- **Customer self-service efficiency** (e.g., chatbots, FAQ retrieval)
- **Internal knowledge management** (e.g., employee portals, document search)
- **Search engine optimization (SEO)** and structured data compliance

This study seeks to provide **data-driven insights** on whether structuring content as **JSON-LD** (used in knowledge graphs) improves information retrieval over **raw HTML** (often used in traditional web search).

---

## Study Design & Methodology

### Content Sources & Formats

This study evaluates the same content in two different formats:

1. **HTML-based FAQ pages**: Generated from Markdown (MD), representing traditional web content.
2. **JSON-LD structured content**: Derived from YAML, adhering to **Schema.org's FAQPage** schema, used in knowledge graphs and AI-driven search systems.

### Evaluation approach
The effectiveness of each format is measured by how accurately it answers **golden dataset questions**—a standardized set of business-relevant queries. The study follows these key steps.

### Step 1: Set up a virtualenv and install the requirements

On a macOS:

```bash
python -m venv ENV
source ./ENV/bin/activate
pip install -r requirements.txt
```

You may need to run `install-nltk-corpus.py` to have access to the training data for the NLTK.

    ```bash
    python install-nltk-corpus.py
    ```

### Step 2: Data preparation

1. Retrieve data from the web with articles that contain both HTML and JSON-LD (FAQPage) payloads.
    Input: A list of URLS.
    Output: Two folders HTML and JSONLD that contain the data.

    For instructions: [Prepare, set-up, and run two vector search pipelines to compare HTML vs JSON-LD](faqpage-scrapper-readme.md)

2. Create the Golden Questions.
    Input: Two folders HTML and JSONLD that contain the data.
    Output: A JSON file of questions to use with both the HTML and JSONLD test.

3. You may want to reduce the number of golden questions to make the assessment more manageable. Make sure you are using the same set for both tests.

### Step 3: Set up Weaviate in a Docker container

Follow the guide that explains how to set up and run Weaviate in a Docker container on macOS. It also covers installing dependencies and verifying the setup. See [Setting Up Weaviate with Docker on macOS](docker_weaviate_readme.md)

### Step 3: Query execution and performance measurement

1. Generate the F1 scores for the golden question set using HTML.

    ```bash
    python html_load_faq_weaviate.py
    ```

1. Generate the F1 scores for the golden question set using JSON-LD.

```bash
python json_load_faq_weaviate.py
```

## Note on the F1 score in this study

Both scripts calculate the F1 score using cosine similarity rather than the traditional precision-recall F1-score. They encode both the retrieved answer (from Weaviate) and the expected answer (from the golden questions dataset) into vector embeddings using SentenceTransformers (`all-MiniLM-L6-v2`) and then compute the cosine similarity between them using `util.pytorch_cos_sim`. This similarity score, ranging from 0 (completely different) to 1 (identical), is treated as the F1 score in the evaluation. The final performance metric is the average cosine similarity across all questions, providing a measure of how well Weaviate retrieves semantically relevant answers.


## Expected Business Insights
This study provides empirical data to help organizations understand:

1. **Does structured JSON-LD data improve AI-powered retrieval?**
   - If JSON-LD (Neo4J) outperforms HTML (Weaviate), it validates that **structured content enhances machine understanding**.
   
2. **How effective is AI-driven vector search for unstructured data?**
   - If Weaviate performs well, businesses may not need full schema compliance for effective AI search.
   
3. **How should businesses structure content for AI-readiness?**
   - The results can help companies **decide on content formatting strategies** for AI-based search, chatbots, and knowledge management systems.

## Conclusion

This study compares **structured vs. unstructured information retrieval** to determine the best strategy for **AI-powered business search applications**. By applying **F1 score measurement**, businesses can make **data-driven decisions** on how to format content for better AI readiness.

The findings can provide **practical recommendations** on:

 - Whether structured **JSON-LD knowledge graphs** should be prioritized over traditional **HTML FAQs**.
 - How **vector search AI** can compensate for **unstructured content**.
 - Best practices for **optimizing enterprise search** using **graph vs. AI-based retrieval**.