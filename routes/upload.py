from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from services.db_service import knowledge_base_collection
from routes.auth import verify_token
from helpers import process_csv_content

router = APIRouter(prefix="/upload")

@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_token)
):
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        
        documents = process_csv_content(csv_content)
        
        if documents:
            result = knowledge_base_collection.insert_many(documents)
            import services.rag_service as rag
            rag.vector_store = None
            rag.vector_store_loaded = False
            
            return {
                "message": f"Successfully uploaded {len(documents)} documents",
                "inserted_count": len(documents)
            }
        else:
            raise HTTPException(status_code=400, detail="No valid data found in CSV")
            
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process upload: {str(e)}")




