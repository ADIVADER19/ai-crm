from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from services.db_service import knowledge_base_collection
from routes.auth import verify_token
from helpers import process_csv_content, process_pdf_content, process_txt_content, process_json_content
import services.rag_service as rag

router = APIRouter(prefix="/upload_docs")

@router.post("/")
async def upload_docs(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_token)
):
    try:
        # check file extension
        allowed_extensions = ['.pdf', '.txt', '.csv', '.json']
        file_extension = None
        for ext in allowed_extensions:
            if file.filename.lower().endswith(ext):
                file_extension = ext
                break
        
        if not file_extension:
            raise HTTPException(
                status_code=400, 
                detail="Only PDF, TXT, CSV, and JSON files are allowed"
            )
        
        contents = await file.read()
        documents = []
        
        # process based on file type
        if file_extension == '.csv':
            csv_content = contents.decode('utf-8')
            documents = process_csv_content(csv_content)
        elif file_extension == '.pdf':
            try:
                documents = process_pdf_content(contents)
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        elif file_extension == '.txt':
            txt_content = contents.decode('utf-8')
            documents = process_txt_content(txt_content)
        elif file_extension == '.json':
            json_content = contents.decode('utf-8')
            try:
                documents = process_json_content(json_content)
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        if documents:
            # clear existing knowledge base
            knowledge_base_collection.delete_many({})
            print(f"Cleared existing knowledge base")
            
            # insert new documents
            result = knowledge_base_collection.insert_many(documents)
            print(f"Inserted {len(documents)} new documents")
            
            # build vector store from the uploaded documents
            vector_store_success = rag.build_vectorstore_from_upload(documents)
            
            if vector_store_success:
                return {
                    "message": f"Successfully uploaded {len(documents)} documents from {file_extension.upper()} file",
                    "inserted_count": len(documents),
                    "file_type": file_extension.replace('.', ''),
                    "vector_store_built": vector_store_success,
                    "note": "Previous knowledge base was replaced with new upload"
                }
            else:
                return {
                    "message": f"Documents uploaded to database but vector store failed to build",
                    "inserted_count": len(documents),
                    "file_type": file_extension.replace('.', ''),
                    "vector_store_built": vector_store_success,
                    "note": "Try uploading a different document. RAG functionality may not work until vector store is built successfully"
                }
        else:
            raise HTTPException(status_code=400, detail=f"No valid data found in {file_extension.upper()} file")
            
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process upload: {str(e)}")