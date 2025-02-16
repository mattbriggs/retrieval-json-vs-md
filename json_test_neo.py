import json
from neo4j import GraphDatabase

# Load credentials from neocred.json
def load_credentials(file_path="neocred.json"):
    try:
        with open(file_path, "r") as file:
            creds = json.load(file)
        return creds["NEO4J_URI"], creds["USERNAME"], creds["PASSWORD"]
    except Exception as e:
        print(f"❌ Failed to load credentials: {e}")
        return None, None, None

# Test connection to Neo4j
def test_neo4j_connection():
    NEO4J_URI, USERNAME, PASSWORD = load_credentials()
    
    if not all([NEO4J_URI, USERNAME, PASSWORD]):
        print("❌ Missing credentials. Check neocred.json.")
        return
    
    try:
        # Connect to Neo4j
        driver = GraphDatabase.driver(NEO4J_URI, auth=(USERNAME, PASSWORD))
        
        # Run a simple query
        with driver.session() as session:
            result = session.run("RETURN '✅ Neo4j connection successful!' AS message")
            for record in result:
                print(record["message"])

        # Close the driver
        driver.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

# Run the test
test_neo4j_connection()
