from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/image")
async def analyze_image(file: UploadFile = File(...)):
    return {"status": "ok", "filename": file.filename, "message": "Image analysis coming soon"}