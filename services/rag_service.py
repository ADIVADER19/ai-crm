from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
collection = client["rentbot"]["knowledge_base"]

embeddings = OpenAIEmbeddings()

vector_store = None
vector_store_loaded = False

def build_vectorstore_from_upload(documents):
    global vector_store, vector_store_loaded
    
    try:
        print(f"Building vector store from {len(documents)} uploaded documents...")
        
        # convert uploaded documents to LangChain Document format
        docs = []
        for doc in documents:
            content = "\n".join([f"{k}: {v}" for k, v in doc.items() if k != "_id"])
            docs.append(Document(page_content=content))

        if docs:
            vector_store = FAISS.from_documents(docs, embeddings)
            vector_store_loaded = True
            print(f"Vector store built successfully with {len(docs)} documents")
            return True
        else:
            print("No valid documents found for vector store")
            return False
            
    except Exception as e:
        print(f"Error building vector store from upload: {e}")
        vector_store = None
        vector_store_loaded = False
        return False

def query_knowledge_base(query: str, k: int = 30):
    global vector_store, vector_store_loaded
    
    try:
        # check if vector store is available
        if not vector_store_loaded or vector_store is None:
            return "No knowledge base available. Please upload documents first using /upload/upload_docs."
        
        results = vector_store.similarity_search(query, k=k)
        return "\n\n".join([doc.page_content for doc in results])
    except Exception as e:
        print(f"Error querying knowledge base: {e}")
        return "Error accessing knowledge base."

# def get_vector_store_status():
#     return {
#         "loaded": vector_store_loaded,
#         "available": vector_store is not None,
#         "document_count": collection.count_documents({}) if collection else 0
#     }
