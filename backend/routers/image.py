from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os

router = APIRouter()

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/tiff"]
MAX_SIZE = 50 * 1024 * 1024  # 50MB

@router.post("/image")
async def analyze_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
    
    contents = await file.read()
    
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")
    
    temp_path = f"temp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)
    
    return {"status": "ok", "filename": file.filename, "size": len(contents), "type": file.content_type}