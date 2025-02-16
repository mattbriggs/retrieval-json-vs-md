import weaviate

client = weaviate.connect_to_local(skip_init_checks=True)  # ✅ Bypass gRPC startup checks

if client.is_ready():
    print("✅ Weaviate is ready!")
else:
    print("❌ Weaviate is not running. Check Docker container.")