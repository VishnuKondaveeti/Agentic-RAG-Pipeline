try:
    from backend.core.agent import AgenticRAG
    print("AgenticRAG imported successfully")
    agent = AgenticRAG()
    print("AgenticRAG initialized successfully")
except Exception as e:
    print(f"Error: {e}")
