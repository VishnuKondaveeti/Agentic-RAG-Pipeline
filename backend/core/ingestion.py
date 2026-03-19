import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
DB_DIR = os.path.join(DATA_DIR, "db")
DOCS_DIR = os.path.join(DATA_DIR, "documents")

# Ensure directories exist
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

def ingest_documents():
    """Load, split, and store documents in ChromaDB."""
    print("Loading documents...")
    loader = DirectoryLoader(DOCS_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    
    if not documents:
        print("No documents found to ingest.")
        return None

    print(f"Loaded {len(documents)} document pages.")

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    print(f"Split into {len(splits)} chunks.")

    # Create embeddings
    print("Generating embeddings (sentence-transformers)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Store in ChromaDB
    print(f"Storing in ChromaDB at {DB_DIR}...")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    print("Ingestion complete.")
    return vectorstore

def get_vectorstore():
    """Load existing vector store."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

if __name__ == "__main__":
    ingest_documents()
