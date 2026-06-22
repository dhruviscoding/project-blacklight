AI_SOFTWARE_SIGNATURES = [
    "stable diffusion", "midjourney", "dall-e", "dalle", "dall·e",
    "firefly", "adobe firefly", "leonardo", "leonardo.ai",
    "runway", "runwayml", "ideogram", "flux", "comfyui",
    "automatic1111", "novelai", "playground ai", "stability ai"
]

EDITING_SOFTWARE_SIGNATURES = [
    "photoshop", "gimp", "lightroom", "affinity photo",
    "pixelmator", "canva", "paint.net"
]


def detect_tampering(raw_metadata: dict) -> dict:
    """
    Scans metadata for signs of AI generation or manual editing tampering.
    Returns a score (0.0-1.0) and findings list.
    """
    findings = []
    score = 0.0

    software = (
        raw_metadata.get("EXIF:Software")
        or raw_metadata.get("XMP:CreatorTool")
        or raw_metadata.get("XMP:Software")
        or ""
    )
    software_lower = software.lower()

    ai_match = next((sig for sig in AI_SOFTWARE_SIGNATURES if sig in software_lower), None)
    editing_match = next((sig for sig in EDITING_SOFTWARE_SIGNATURES if sig in software_lower), None)

    if ai_match:
        findings.append(f"Software tag indicates AI generation tool: '{software}'")
        score = 1.0
    elif editing_match:
        findings.append(f"Software tag indicates editing tool: '{software}'")
        score = 0.5
    elif software:
        findings.append(f"Software tag present: '{software}' (not a known AI generator)")
        score = 0.1
    else:
        findings.append("No software tag present in metadata")
        score = 0.0

    # Check for completely stripped metadata (common with AI tools and re-saved/exported images)
    has_camera_info = bool(
        raw_metadata.get("EXIF:Make") or raw_metadata.get("EXIF:Model")
    )
    has_exif_fields = len([k for k in raw_metadata.keys() if k.startswith("EXIF:")])

    if not has_camera_info and has_exif_fields < 3:
        findings.append("No camera metadata present — inconclusive (common in social media downloads, screenshots, and AI exports alike)")
        score = max(score, 0.5)

    return {
        "software_detected": software if software else None,
        "ai_tool_match": ai_match,
        "editing_tool_match": editing_match,
        "score": round(score, 2),
        "findings": findings
    }