# Setting Up Weaviate with Docker on macOS

This guide explains how to set up and run Weaviate in a Docker container on macOS. It also covers installing dependencies and verifying the setup.

---

## **Prerequisites**
Ensure you have the following installed on your macOS system:
- **Docker** ([Download Here](https://www.docker.com/get-started/))
- **Python 3.8+** ([Download Here](https://www.python.org/downloads/))

To check if Docker is installed, run:
```sh
docker --version
```
If Docker is not installed, download and install it from the link above.

---

## **Step 1: Start Weaviate Using Docker**

Run the following command to pull and start Weaviate with OpenAI text vectorization:
```sh
docker run -d --rm --name weaviate -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
    -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
    -e QUERY_DEFAULTS_LIMIT=25 \
    -e ENABLE_MODULES=text2vec-openai \
    -e OPENAI_APIKEY=<your-openai-key> \
    -p 8080:8080 semitechnologies/weaviate:1.22.1
```
Replace `<your-openai-key>` with your OpenAI API key.

To verify Weaviate is running, execute:
```sh
docker ps | grep weaviate
```
You should see a running Weaviate container.

---

## **Step 2: Install Python Dependencies**

To interact with Weaviate, install the required Python packages:
```sh
pip install weaviate-client
```
To verify installation:
```sh
python -c "import weaviate; print('Weaviate client installed successfully')"
```

---

## **Step 3: Test Connection to Weaviate**
Create a Python script (`test_weaviate.py`) to verify connectivity:
```python
import weaviate

client = weaviate.Client("http://localhost:8080")

if client.is_ready():
    print("✅ Weaviate is ready!")
else:
    print("❌ Weaviate is not running. Check Docker container.")
```
Run the script:
```sh
python test_weaviate.py
```
If successful, you should see:
```sh
✅ Weaviate is ready!
```

---

## **Step 4: Stop and Restart Weaviate**
To stop Weaviate, run:
```sh
docker stop weaviate
```
To restart Weaviate, run the original `docker run` command again.

---

## **Troubleshooting**
### **1. Docker is not running**
Run:
```sh
open -a Docker
```
Wait for Docker to fully start, then retry running Weaviate.

### **2. Port 8080 is in use**
Check if another process is using port 8080:
```sh
lsof -i :8080
```
If occupied, stop the process or run Weaviate on a different port (`-p 9090:8080`).

---

## **Next Steps**
You now have Weaviate running in Docker on macOS. Next, you can:
- Load data into Weaviate
- Perform vector searches
- Integrate with AI models for semantic retrieval

For more details, visit [Weaviate Documentation](https://weaviate.io/developers/weaviate).

