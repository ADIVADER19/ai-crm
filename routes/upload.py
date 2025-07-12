from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import pandas as pd
import io
from services.db_service import db
from routes.auth import verify_token
from typing import List

router = APIRouter(prefix="/upload")

@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    collection_name: str = "knowledge_base",
    user_id: str = Depends(verify_token)
):
    """Upload CSV file and store data in MongoDB collection"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Convert DataFrame to records
        records = df.to_dict(orient="records")
        
        # Add metadata
        for record in records:
            record["uploaded_by"] = user_id
            record["upload_timestamp"] = pd.Timestamp.now()
        
        # Insert into MongoDB
        collection = db[collection_name]
        result = collection.insert_many(records)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Successfully uploaded {len(records)} records",
                "collection": collection_name,
                "inserted_ids": [str(id) for id in result.inserted_ids[:5]]  # Show first 5 IDs
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/knowledge-base")
async def upload_knowledge_base(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_token)
):
    """Upload CSV file specifically for knowledge base"""
    return await upload_csv(file, "knowledge_base", user_id)

@router.get("/collections")
async def list_collections(user_id: str = Depends(verify_token)):
    """List all available collections"""
    try:
        collections = db.list_collection_names()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing collections: {str(e)}")

@router.get("/collection/{collection_name}/count")
async def get_collection_count(
    collection_name: str,
    user_id: str = Depends(verify_token)
):
    """Get document count for a specific collection"""
    try:
        collection = db[collection_name]
        count = collection.count_documents({})
        return {"collection": collection_name, "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting count: {str(e)}")

@router.delete("/collection/{collection_name}")
async def clear_collection(
    collection_name: str,
    user_id: str = Depends(verify_token)
):
    """Clear all documents from a collection"""
    try:
        collection = db[collection_name]
        result = collection.delete_many({})
        return {
            "message": f"Cleared {result.deleted_count} documents from {collection_name}",
            "deleted_count": result.deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing collection: {str(e)}")
