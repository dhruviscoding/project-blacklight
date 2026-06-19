from PIL import Image, ImageChops
import numpy as np
import io
import base64


def analyze_ela(file_path: str, quality: int = 95) -> dict:
    """
    Performs Error Level Analysis (ELA) on an image.
    Resaves the image at a known JPEG quality and measures pixel-level
    differences. Uniform error levels across the whole image are a
    signal of AI generation or single-pass export (no edit history).
    """
    original = Image.open(file_path).convert("RGB")

    # Resave into memory at known quality
    buffer = io.BytesIO()
    original.save(buffer, "JPEG", quality=quality)
    buffer.seek(0)
    resaved = Image.open(buffer)

    # Compute absolute difference between original and resaved
    diff = ImageChops.difference(original, resaved)
    diff_array = np.array(diff)

    # Amplify for visibility
    amplified = np.clip(diff_array * 10, 0, 255).astype(np.uint8)

    mean_error = float(np.mean(diff_array))
    std_error = float(np.std(diff_array))

    # High uniformity (low std relative to mean) suggests single-pass export
    uniformity_ratio = std_error / (mean_error + 1e-6)

    # Score logic: low uniformity ratio = single-pass export pattern
    # NOTE: ELA is primarily a splice/manipulation detector in forensic literature.
    # As a standalone AI-generation signal it is weak — used here only as a
    # weak corroborating signal (low weight in verdict engine), not a primary one.
    if uniformity_ratio < 0.8:
        score = 0.7
        finding = "Uniform compression error levels — consistent with single-pass export (weak corroborating signal, not conclusive alone)"
    elif uniformity_ratio < 1.2:
        score = 0.4
        finding = "Moderately uniform compression error levels — inconclusive"
    else:
        score = 0.15
        finding = "Variable compression error levels — consistent with natural edit/save history"

    # Encode amplified diff image as base64 for frontend visualization
    ela_image = Image.fromarray(amplified)
    out_buffer = io.BytesIO()
    ela_image.save(out_buffer, format="PNG")
    ela_base64 = base64.b64encode(out_buffer.getvalue()).decode("utf-8")

    return {
        "name": "Error Level Analysis",
        "category": "Statistical",
        "score": score,
        "finding": finding,
        "raw_data": {
            "mean_error": round(mean_error, 4),
            "std_error": round(std_error, 4),
            "uniformity_ratio": round(uniformity_ratio, 4)
        },
        "visualization": f"data:image/png;base64,{ela_base64}"
    }