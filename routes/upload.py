from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import csv
from io import StringIO
from services.db_service import knowledge_base_collection
from routes.auth import verify_token

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
        
        csv_reader = csv.DictReader(StringIO(csv_content))
        documents = []
        
        for row in csv_reader:
            doc = {k.strip(): v.strip() for k, v in row.items() if v.strip()}
            if doc:
                documents.append(doc)
        
        if documents:
            result = knowledge_base_collection.insert_many(documents)
            
            # Reset vector store to force rebuild on next query
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




