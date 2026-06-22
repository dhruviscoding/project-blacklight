from fastapi import APIRouter, UploadFile, File, HTTPException
from analyzers.video.video_metadata import analyze_video_metadata
from analyzers.video.keyframe_extractor import extract_keyframes
from analyzers.metadata.exif_analyzer import get_full_metadata_signal
from analyzers.integrity.c2pa_verifier import verify_c2pa
from analyzers.ai_detection.ela_analyzer import analyze_ela
from analyzers.ai_detection.fft_analyzer import analyze_fft
from analyzers.ai_detection.noise_analyzer import analyze_noise
from analyzers.ai_detection.image_classifier import analyze_cnn
from analyzers.ai_detection.modern_classifier import analyze_modern_cnn
from engines.verdict_engine import run_verdict_engine
import os

router = APIRouter()

ALLOWED_VIDEO_TYPES = ["video/mp4", "video/quicktime", "video/x-msvideo"]
MAX_SIZE = 50 * 1024 * 1024


@router.post("/video")
async def analyze_video(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    contents = await file.read()

    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")

    temp_path = f"temp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)

    # Extract container metadata
    video_metadata = {}
    try:
        video_metadata = analyze_video_metadata(temp_path)
    except Exception as e:
        video_metadata = {"error": str(e)}

    # Extract keyframes
    frames = []
    try:
        frames = extract_keyframes(temp_path, interval_seconds=5)
    except Exception as e:
        frames = []

    if not frames:
        return {
            "status": "ok",
            "filename": file.filename,
            "file_type": file.content_type,
            "video_metadata": video_metadata,
            "verdict": {
                "verdict": "INCONCLUSIVE",
                "confidence": None,
                "risk_level": "UNKNOWN",
                "note": "No keyframes could be extracted from this video"
            },
            "frame_results": []
        }

    # Run full image pipeline on each keyframe
    frame_results = []
    for frame_path in frames[:10]:  # cap at 10 frames to avoid timeout
        frame_verdict = {}
        try:
            signals = {}
            try:
                signals["metadata"] = get_full_metadata_signal(frame_path)
            except:
                signals["metadata"] = None
            try:
                signals["c2pa"] = verify_c2pa(frame_path)
            except:
                signals["c2pa"] = None
            try:
                signals["ela"] = analyze_ela(frame_path)
            except:
                signals["ela"] = None
            try:
                signals["fft"] = analyze_fft(frame_path)
            except:
                signals["fft"] = None
            try:
                signals["noise"] = analyze_noise(frame_path)
            except:
                signals["noise"] = None
            try:
                signals["cnn"] = analyze_cnn(frame_path)
            except:
                signals["cnn"] = None
            try:
                signals["vit"] = analyze_modern_cnn(frame_path)
            except:
                signals["vit"] = None

            frame_verdict = run_verdict_engine(signals)
        except Exception as e:
            frame_verdict = {"verdict": "FAILED", "error": str(e)}

        frame_results.append({
            "frame": os.path.basename(frame_path),
            "verdict": frame_verdict
        })

    # Aggregate frame verdicts
    valid_confidences = [
        r["verdict"]["confidence"]
        for r in frame_results
        if r["verdict"].get("confidence") is not None
    ]

    if valid_confidences:
        avg_confidence = sum(valid_confidences) / len(valid_confidences)
        flagged_frames = sum(1 for c in valid_confidences if c > 0.6)

        if avg_confidence >= 0.80:
            agg_verdict = "AI GENERATED"
            risk = "CRITICAL"
        elif avg_confidence >= 0.60:
            agg_verdict = "LIKELY AI GENERATED"
            risk = "HIGH"
        elif avg_confidence >= 0.35:
            agg_verdict = "INCONCLUSIVE"
            risk = "MEDIUM"
        else:
            agg_verdict = "LIKELY AUTHENTIC"
            risk = "LOW"
    else:
        avg_confidence = None
        flagged_frames = 0
        agg_verdict = "INCONCLUSIVE"
        risk = "UNKNOWN"

    return {
        "status": "ok",
        "filename": file.filename,
        "file_type": file.content_type,
        "video_metadata": video_metadata,
        "verdict": {
            "verdict": agg_verdict,
            "confidence": round(avg_confidence, 4) if avg_confidence else None,
            "risk_level": risk,
            "frames_analyzed": len(frame_results),
            "frames_flagged": flagged_frames,
            "note": "Video verdict based on per-frame image analysis. Deepfake-specific temporal analysis coming in Phase 2."
        },
        "frame_results": frame_results
    }