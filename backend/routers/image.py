from fastapi import APIRouter, UploadFile, File, HTTPException
from analyzers.metadata.exif_analyzer import get_full_metadata_signal
from analyzers.integrity.hash_generator import generate_hashes
from analyzers.integrity.perceptual_hash import generate_perceptual_hashes
from analyzers.integrity.c2pa_verifier import verify_c2pa
from analyzers.integrity.reverse_search_links import generate_reverse_search_links
from analyzers.ai_detection.ela_analyzer import analyze_ela
from analyzers.ai_detection.fft_analyzer import analyze_fft
from analyzers.ai_detection.noise_analyzer import analyze_noise
from analyzers.ai_detection.image_classifier import analyze_cnn
from analyzers.ai_detection.modern_classifier import analyze_modern_cnn
from engines.verdict_engine import run_verdict_engine
import os

router = APIRouter()

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/tiff"]
MAX_SIZE = 50 * 1024 * 1024


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

    results = {}

    # Run each analyzer independently — if one crashes, log and continue
    try:
        results["metadata"] = get_full_metadata_signal(temp_path)
    except Exception as e:
        results["metadata"] = {"name": "Metadata Analysis", "score": None, "finding": f"Failed: {e}"}

    try:
        results["hashes"] = {
            "cryptographic": generate_hashes(temp_path),
            "perceptual": generate_perceptual_hashes(temp_path)
        }
    except Exception as e:
        results["hashes"] = None

    try:
        results["c2pa"] = verify_c2pa(temp_path)
    except Exception as e:
        results["c2pa"] = {"name": "C2PA Verification", "score": None, "finding": f"Failed: {e}"}

    try:
        results["ela"] = analyze_ela(temp_path)
    except Exception as e:
        results["ela"] = {"name": "Error Level Analysis", "score": None, "finding": f"Failed: {e}"}

    try:
        results["fft"] = analyze_fft(temp_path)
    except Exception as e:
        results["fft"] = {"name": "FFT Frequency Analysis", "score": None, "finding": f"Failed: {e}"}

    try:
        results["noise"] = analyze_noise(temp_path)
    except Exception as e:
        results["noise"] = {"name": "Noise Analysis", "score": None, "finding": f"Failed: {e}"}

    try:
        results["cnn"] = analyze_cnn(temp_path)
    except Exception as e:
        results["cnn"] = {"name": "CNN Classifier", "score": None, "finding": f"Failed: {e}"}

    try:
        results["vit"] = analyze_modern_cnn(temp_path)
    except Exception as e:
        results["vit"] = {"name": "Modern AI Classifier", "score": None, "finding": f"Failed: {e}"}

    # Reverse search links — stub until Supabase storage gives us public URLs
    results["reverse_search"] = generate_reverse_search_links(
        f"https://placeholder.blacklight.app/temp/{file.filename}"
    )

    # Run verdict engine
    verdict = run_verdict_engine({
        "c2pa": results["c2pa"],
        "cnn": results["cnn"],
        "vit": results["vit"],
        "fft": results["fft"],
        "noise": results["noise"],
        "metadata": results["metadata"],
        "ela": results["ela"]
    })

    return {
        "status": "ok",
        "filename": file.filename,
        "file_type": file.content_type,
        "verdict": verdict,
        "signals": {
            "metadata": results["metadata"],
            "hashes": results["hashes"],
            "c2pa": results["c2pa"],
            "ela": results["ela"],
            "fft": results["fft"],
            "noise": results["noise"],
            "cnn": results["cnn"],
            "vit": results["vit"]
        },
        "reverse_search": results["reverse_search"]
    }