from fastapi import APIRouter, UploadFile, File, HTTPException
from analyzers.audio.audio_metadata import analyze_audio_metadata
from analyzers.audio.spectral_analyzer import analyze_audio_spectral

router = APIRouter()

ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/wav", "audio/flac", "audio/x-wav"]
MAX_SIZE = 50 * 1024 * 1024


@router.post("/audio")
async def analyze_audio(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    contents = await file.read()

    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")

    temp_path = f"temp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)

    metadata = {}
    spectral = {}

    try:
        metadata = analyze_audio_metadata(temp_path)
    except Exception as e:
        metadata = {"error": str(e)}

    try:
        spectral = analyze_audio_spectral(temp_path)
    except Exception as e:
        spectral = {"error": str(e)}

    return {
        "status": "ok",
        "filename": file.filename,
        "file_type": file.content_type,
        "preliminary_analysis": {
            "metadata": metadata,
            "spectral": spectral
        },
        "verdict": {
            "verdict": "PRELIMINARY ANALYSIS ONLY",
            "confidence": None,
            "risk_level": "UNKNOWN",
            "note": "Full AI voice detection coming in Phase 2 — resemblyzer, speechbrain, vocoder artifact detection"
        }
    }