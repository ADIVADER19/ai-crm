from bson import ObjectId
import os
import csv
import jwt
import datetime
import json
import PyPDF2
import io
from io import StringIO
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM")


def convert_objectid_to_str(doc):
    if doc is None:
        return None
    
    if isinstance(doc, ObjectId):
        return str(doc)
    
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, dict):
                result[key] = convert_objectid_to_str(value)
            elif isinstance(value, list):
                result[key] = [convert_objectid_to_str(item) for item in value]
            else:
                result[key] = value
        return result
    
    if isinstance(doc, list):
        return [convert_objectid_to_str(item) for item in doc]
    
    return doc


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token_payload(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise jwt.InvalidTokenError("Invalid token: no user_id")
        return user_id
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token")


def classify_message_category(user_input: str) -> str:
    try:
        classification_prompt = [
            {
                "role": "system",
                "content": """You are a category classifier for a real estate CRM system. 
                
Classify the user's message into ONE of these categories:
- property_search: User is looking for properties, asking about rentals, spaces, or specific property details
- general_inquiry: General questions about real estate, market info, or company services  
- support: Technical issues, account problems, or help requests
- pricing_inquiry: Questions specifically about pricing, costs, fees, or budget discussions
- property_details: Asking for specific details about a particular property
- general: Default category for unclear or social messages

Respond with ONLY the category name, nothing else."""
            },
            {
                "role": "user", 
                "content": user_input
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=classification_prompt,
            max_tokens=20,
            temperature=0.1  # low temperature for consistent classification
        )
        
        category = response.choices[0].message.content.strip().lower()
        
        # validate category is one of our allowed categories
        valid_categories = ["property_search", "general_inquiry", "support", "pricing_inquiry", "property_details", "general"]
        if category not in valid_categories:
            category = "general"
            
        print(f"Classified message category: {category}")
        return category
        
    except Exception as e:
        print(f"Error classifying category: {e}")
        return "general"  # Default fallback


def process_csv_content(csv_content: str) -> list:
    try:
        csv_reader = csv.DictReader(StringIO(csv_content))
        documents = []
        
        for row in csv_reader:
            doc = {k.strip(): v.strip() for k, v in row.items() if v.strip()}
            if doc:
                documents.append(doc)
        
        return documents
    except Exception as e:
        print(f"Error processing CSV content: {e}")
        return []


def process_pdf_content(file_content: bytes) -> list:
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"
        
        chunks = [text_content[i:i+1000] for i in range(0, len(text_content), 1000)]
        documents = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                documents.append({
                    "content": chunk.strip(),
                    "type": "pdf",
                    "chunk_id": i
                })
        return documents
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")

def process_txt_content(file_content: str) -> list:
    chunks = [file_content[i:i+1000] for i in range(0, len(file_content), 1000)]
    documents = []
    for i, chunk in enumerate(chunks):
        if chunk.strip():
            documents.append({
                "content": chunk.strip(),
                "type": "txt",
                "chunk_id": i
            })
    return documents

def process_json_content(file_content: str) -> list:
    try:
        data = json.loads(file_content)
        documents = []
        
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    content = json.dumps(item, indent=2)
                else:
                    content = str(item)
                documents.append({
                    "content": content,
                    "type": "json",
                    "item_id": i
                })
        elif isinstance(data, dict):
            content = json.dumps(data, indent=2)
            documents.append({
                "content": content,
                "type": "json",
                "item_id": 0
            })
        else:
            documents.append({
                "content": str(data),
                "type": "json",
                "item_id": 0
            })
        
        return documents
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON format: {str(e)}")
