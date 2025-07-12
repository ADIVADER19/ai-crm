from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from pymongo import MongoClient
import os
import pickle
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
collection = client["rentbot"]["knowledge_base"]

# Cache directory for storing the vector store
CACHE_DIR = Path("cache")
VECTOR_STORE_PATH = CACHE_DIR / "vector_store"
METADATA_PATH = CACHE_DIR / "vector_store_metadata.pkl"

embeddings = OpenAIEmbeddings()

# Cache the vector store in memory
vector_store = None
vector_store_loaded = False

def check_vector_store_exists():
    """Check if a pre-built vector store exists on disk"""
    return VECTOR_STORE_PATH.exists() and METADATA_PATH.exists()

def get_current_data_hash():
    """Get a hash of current knowledge base data to check for changes"""
    try:
        # Get total count and a sample of document IDs to create a simple signature
        doc_count = collection.count_documents({})
        sample_docs = list(collection.find({}, {"_id": 1}).limit(10))
        
        # Create a simple signature based on count and sample document IDs
        signature = f"{doc_count}_{len(sample_docs)}"
        if sample_docs:
            signature += "_" + "_".join([str(doc["_id"]) for doc in sample_docs[:5]])
        
        return signature
    except Exception as e:
        print(f"Error getting data hash: {e}")
        return None

def save_vector_store_metadata(data_hash, doc_count):
    """Save metadata about the vector store"""
    CACHE_DIR.mkdir(exist_ok=True)
    metadata = {
        "data_hash": data_hash,
        "doc_count": doc_count,
        "created_at": os.getcwd()  # Simple timestamp alternative
    }
    with open(METADATA_PATH, 'wb') as f:
        pickle.dump(metadata, f)

def load_vector_store_metadata():
    """Load metadata about the existing vector store"""
    try:
        with open(METADATA_PATH, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return None

def load_existing_vector_store():
    """Load an existing vector store from disk"""
    global vector_store, vector_store_loaded
    
    try:
        print("Loading existing vector store from cache...")
        vector_store = FAISS.load_local(str(VECTOR_STORE_PATH), embeddings, allow_dangerous_deserialization=True)
        vector_store_loaded = True
        
        metadata = load_vector_store_metadata()
        if metadata:
            print(f"✓ Vector store loaded with {metadata.get('doc_count', 'unknown')} documents from cache")
        else:
            print("✓ Vector store loaded from cache (metadata unavailable)")
        return True
    except Exception as e:
        print(f"Error loading existing vector store: {e}")
        return False

def save_vector_store():
    """Save the current vector store to disk"""
    global vector_store
    
    if vector_store is None:
        return False
    
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        vector_store.save_local(str(VECTOR_STORE_PATH))
        print("✓ Vector store saved to cache")
        return True
    except Exception as e:
        print(f"Error saving vector store: {e}")
        return False

def build_vectorstore():
    global vector_store, vector_store_loaded
    
    # If already loaded in memory, don't rebuild
    if vector_store_loaded and vector_store is not None:
        print("✓ Vector store already loaded in memory")
        return True
    
    # Check if we can load from cache
    if check_vector_store_exists():
        current_hash = get_current_data_hash()
        metadata = load_vector_store_metadata()
        
        # If data hasn't changed, load from cache
        if metadata and metadata.get('data_hash') == current_hash:
            print("✓ Knowledge base data unchanged, loading from cache...")
            if load_existing_vector_store():
                return True
        else:
            print("Knowledge base data has changed, rebuilding vector store...")
    
    # Build new vector store
    try:
        print("Building new vector store from MongoDB...")

        docs = []
        doc_count = collection.count_documents({})
        if doc_count == 0:
            print("Warning: No documents found in knowledge base collection")
            return False

        for doc in collection.find():
            # You can customize how text is composed here
            content = "\n".join([f"{k}: {v}" for k, v in doc.items() if k != "_id"])
            docs.append(Document(page_content=content))

        if docs:
            vector_store = FAISS.from_documents(docs, embeddings)
            vector_store_loaded = True
            print(f"✓ Vector store built with {len(docs)} documents")
            
            # Save to cache for future use
            save_vector_store()
            
            # Save metadata
            current_hash = get_current_data_hash()
            if current_hash:
                save_vector_store_metadata(current_hash, doc_count)
            
            return True
        else:
            print("No valid documents found for vector store")
            return False
            
    except Exception as e:
        print(f"Error building vector store: {e}")
        print("Note: This might be due to OpenAI API quota limits. The server will continue without RAG functionality.")
        vector_store = None
        vector_store_loaded = False
        return False

def query_knowledge_base(query: str, k: int = 3):
    global vector_store, vector_store_loaded
    
    try:
        # Only try to build if not already loaded
        if not vector_store_loaded or vector_store is None:
            print("Vector store not ready, attempting to initialize...")
            if not build_vectorstore():
                return "Knowledge base is currently unavailable. Please try again later."
        
        if vector_store is None:
            return "No knowledge base available. Please upload data first."

        results = vector_store.similarity_search(query, k=k)
        return "\n\n".join([doc.page_content for doc in results])
    except Exception as e:
        print(f"Error querying knowledge base: {e}")
        return "Error accessing knowledge base."

def get_vector_store_status():
    """Get the current status of the vector store"""
    return {
        "loaded": vector_store_loaded,
        "available": vector_store is not None,
        "cache_exists": check_vector_store_exists(),
        "cache_path": str(VECTOR_STORE_PATH) if VECTOR_STORE_PATH.exists() else None
    }
