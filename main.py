import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import DocumentQC

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Document QC API is running"}

# Helper to convert ObjectId and datetime to JSON-serializable
from datetime import datetime

def _serialize_doc(doc: dict):
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out

# Request model for bulk insert
class DocumentQCBulkIn(BaseModel):
    items: List[DocumentQC]

@app.post("/api/qc/bulk")
def import_qc_results(payload: DocumentQCBulkIn):
    """Bulk import QC results into the database"""
    inserted_ids = []
    for item in payload.items:
        # If is_complete not provided, infer from missing_sections
        data = item.model_dump()
        if data.get("is_complete") is None:
            missing = data.get("missing_sections") or []
            data["is_complete"] = len(missing) == 0
        inserted_id = create_document("documentqc", data)
        inserted_ids.append(inserted_id)
    return {"inserted": len(inserted_ids), "ids": inserted_ids}

@app.get("/api/qc")
def list_qc(
    search: Optional[str] = Query(None, description="Search by document_id or filename"),
    complete: Optional[bool] = Query(None, description="Filter by completeness"),
    missing: Optional[bool] = Query(None, description="Only documents with missing sections"),
    limit: int = Query(200, ge=1, le=1000)
):
    """List QC results with optional filters"""
    filter_dict = {}
    if complete is not None:
        filter_dict["is_complete"] = complete
    if missing is True:
        filter_dict["missing_sections.0"] = {"$exists": True}
    if search:
        filter_dict["$or"] = [
            {"document_id": {"$regex": search, "$options": "i"}},
            {"filename": {"$regex": search, "$options": "i"}},
        ]

    docs = get_documents("documentqc", filter_dict, limit)
    return [_serialize_doc(d) for d in docs]

@app.get("/api/qc/{doc_id}")
def get_qc(doc_id: str):
    doc = db["documentqc"].find_one({"_id": ObjectId(doc_id)}) if ObjectId.is_valid(doc_id) else db["documentqc"].find_one({"document_id": doc_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _serialize_doc(doc)

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
