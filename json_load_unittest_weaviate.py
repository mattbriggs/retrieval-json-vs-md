import unittest
import weaviate
import subprocess

WEAVIATE_CONTAINER = "weaviate"  # Ensure this matches your Weaviate container name
COLLECTION_NAME = "FAQ"

# ==============================================================
# UNIT TEST CLASS
# ==============================================================

class TestWeaviateSetup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up Weaviate client and collection before running tests."""
        cls.client = weaviate.connect_to_local()
        cls.collection = cls.client.collections.get(COLLECTION_NAME)

    @classmethod
    def tearDownClass(cls):
        """Close Weaviate client after all tests."""
        cls.client.close()

    # ==============================================================
    # TEST 1: CHECK IF WEAVIATE IS RUNNING
    # ==============================================================
    def test_1_weaviate_running(self):
        """Test if Weaviate is running and accessible."""
        self.assertTrue(self.client.is_ready(), "❌ Weaviate is not running or accessible.")

    # ==============================================================
    # TEST 2: CHECK OPENAI API KEY PROPAGATION
    # ==============================================================
    def test_2_openai_api_key_propagation(self):
        """Test if OpenAI API Key is being used by Weaviate."""
        try:
            result = subprocess.run(
                ["docker", "exec", WEAVIATE_CONTAINER, "env"],
                capture_output=True,
                text=True,
                check=True,
            )

            api_key = None
            for line in result.stdout.split("\n"):
                if "OPENAI_APIKEY=" in line:
                    api_key = line.split("=")[1].strip()

            self.assertIsNotNone(api_key, "❌ OpenAI API Key is missing in Weaviate!")

        except subprocess.CalledProcessError:
            self.fail("❌ Unable to retrieve API key from Weaviate container.")

    # ==============================================================
    # TEST 3: CHECK IF COLLECTION EXISTS
    # ==============================================================
    def test_3_collection_exists(self):
        """Test if the 'FAQ' collection exists in Weaviate."""
        existing_collections = self.client.collections.list_all()
        self.assertIn(COLLECTION_NAME, existing_collections, f"❌ Collection '{COLLECTION_NAME}' does not exist.")

    # ==============================================================
    # TEST 4: CHECK DATA INSERTION
    # ==============================================================
    def test_4_data_insertion(self):
        """Test if FAQ data has been inserted into Weaviate."""
        # ✅ Fix: Use `fetch_objects()` to retrieve objects
        response = self.collection.query.fetch_objects()
        data_objects = response.objects if response else []

        self.assertGreater(len(data_objects), 0, "❌ No FAQ data found in Weaviate.")

    # ==============================================================
    # TEST 5: CHECK QUERY FUNCTIONALITY
    # ==============================================================
    def test_5_query_weaviate(self):
        """Test if querying Weaviate returns results."""
        question = "Is Azure Synapse Link for SQL generally available?"

        # ✅ Fix: Use `near_text` correctly
        response = self.collection.query.near_text(question, limit=1)

        result = response.objects if response else []
        self.assertGreater(len(result), 0, "❌ Query returned no results.")

if __name__ == "__main__":
    unittest.main()