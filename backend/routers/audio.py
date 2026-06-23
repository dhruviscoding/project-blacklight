from fastapi import APIRouter, UploadFile, File, HTTPException
from analyzers.audio.audio_metadata import analyze_audio_metadata
from analyzers.audio.spectral_analyzer import analyze_audio_spectral
from analyzers.audio.edit_detector import detect_edit_artifacts
from analyzers.audio.speaker_analyzer import analyze_speaker_consistency
from analyzers.integrity.hash_generator import generate_hashes

router = APIRouter()

ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/wav", "audio/flac", "audio/x-wav", "audio/mp4", "audio/x-m4a"]
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

    results = {}

    try:
        results["metadata"] = analyze_audio_metadata(temp_path)
    except Exception as e:
        results["metadata"] = {"error": str(e)}

    try:
        results["hashes"] = generate_hashes(temp_path)
    except Exception as e:
        results["hashes"] = {"error": str(e)}

    try:
        results["spectral"] = analyze_audio_spectral(temp_path)
    except Exception as e:
        results["spectral"] = {"error": str(e)}

    try:
        results["edit_artifacts"] = detect_edit_artifacts(temp_path)
    except Exception as e:
        results["edit_artifacts"] = {"error": str(e)}

    try:
        results["speaker_consistency"] = analyze_speaker_consistency(temp_path)
    except Exception as e:
        results["speaker_consistency"] = {"error": str(e)}

    # Build forensic assessment
    findings = []
    synthesis_indicators = results.get("spectral", {}).get("synthesis_indicators", [])
    edit_findings = results.get("edit_artifacts", {}).get("findings", [])
    speaker_finding = results.get("speaker_consistency", {}).get("finding", "")
    speaker_consistent = results.get("speaker_consistency", {}).get("consistent")

    if synthesis_indicators:
        findings.extend(synthesis_indicators)
    if results.get("edit_artifacts", {}).get("edit_artifacts_detected"):
        findings.extend(edit_findings)
    if speaker_consistent is False:
        findings.append(speaker_finding)

    if not findings:
        findings.append("No significant forensic anomalies detected in audio")

    # Synthesis likelihood score based on available signals
    score_components = []
    spectral = results.get("spectral", {})

    # Rough speech vs music detection
    # Music has high spectral centroid (>3000Hz typically) and many synthesis
    # indicators don't apply to music — skip HNR and level checks for music
    is_likely_music = False
    metadata = results.get("metadata", {})
    duration = spectral.get("duration_seconds", 0)
    num_pauses = spectral.get("silence", {}).get("num_pauses", 0)
    edit_count = len(results.get("edit_artifacts", {}).get("level_discontinuities", []))

    # Heuristic: music tends to have many level changes relative to pauses
    if duration > 10 and edit_count > 50 and num_pauses > 10:
        is_likely_music = True

    if spectral.get("pitch", {}).get("flatness_index") is not None:
        pitch_flatness = spectral["pitch"]["flatness_index"]
        score_components.append(0.75 if pitch_flatness < 0.15 else 0.2)

    if spectral.get("silence", {}).get("silence_ratio") is not None:
        silence_ratio = spectral["silence"]["silence_ratio"]
        score_components.append(0.7 if silence_ratio < 0.02 else 0.2)

    # HNR removed from scoring — too much overlap between compressed real speech
    # and TTS in real-world conditions. Still reported as a metric for investigators.
    if speaker_consistent is False:
        score_components.append(0.8)
    elif speaker_consistent is True:
        score_components.append(0.1)
    if results.get("edit_artifacts", {}).get("edit_artifacts_detected"):
        score_components.append(0.6)

    synthesis_likelihood = sum(score_components) / len(score_components) if score_components else None

    if synthesis_likelihood is not None:
        if synthesis_likelihood > 0.6:
            assessment = "HIGH — Multiple indicators of synthetic or manipulated audio"
            risk = "HIGH"
        elif synthesis_likelihood > 0.35:
            assessment = "MEDIUM — Some indicators present, manual review recommended"
            risk = "MEDIUM"
        else:
            assessment = "LOW — No strong indicators of synthesis or manipulation"
            risk = "LOW"
    else:
        assessment = "INCONCLUSIVE — Insufficient data for assessment"
        risk = "UNKNOWN"

    # Note for music/non-speech content
    content_note = None
    if is_likely_music:
        content_note = "Note: Audio characteristics suggest this may be music or non-speech content. HNR and level-based indicators are optimized for speech — results may not be meaningful for music files."

    return {
        "status": "ok",
        "filename": file.filename,
        "file_type": file.content_type,
        "forensic_assessment": {
            "synthesis_likelihood": round(synthesis_likelihood, 4) if synthesis_likelihood else None,
            "risk_level": risk,
            "assessment": assessment,
            "findings": findings,
            "content_note": content_note
        },
        "signals": {
            "metadata": results["metadata"],
            "hashes": results["hashes"],
            "spectral": results["spectral"],
            "edit_artifacts": results["edit_artifacts"],
            "speaker_consistency": results["speaker_consistency"]
        }
    }