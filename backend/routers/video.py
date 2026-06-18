from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/video")
async def analyze_video(file: UploadFile = File(...)):
    return {"status": "ok", "filename": file.filename, "message": "Video analysis coming soon"}