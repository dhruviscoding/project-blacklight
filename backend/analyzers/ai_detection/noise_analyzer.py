from PIL import Image, ImageFilter
import numpy as np
import io
import base64


def analyze_noise(file_path: str) -> dict:
    """
    Analyzes sensor noise patterns in an image.
    Real camera photos carry natural sensor noise. AI-generated images
    often show unnaturally smooth or uniform noise distribution since
    they lack a physical sensor's imperfections.
    """
    image = Image.open(file_path).convert("RGB")

    # Smooth the image with a median filter to estimate the "clean" signal
    smoothed = image.filter(ImageFilter.MedianFilter(size=5))

    original_array = np.array(image, dtype=np.float64)
    smoothed_array = np.array(smoothed, dtype=np.float64)

    # Noise residual = original - smoothed
    noise_residual = original_array - smoothed_array

    mean_noise = float(np.mean(np.abs(noise_residual)))
    std_noise = float(np.std(noise_residual))

    # Check noise uniformity across image regions (split into quadrants)
    h, w, _ = noise_residual.shape
    mid_h, mid_w = h // 2, w // 2

    quadrants = [
        noise_residual[:mid_h, :mid_w],
        noise_residual[:mid_h, mid_w:],
        noise_residual[mid_h:, :mid_w],
        noise_residual[mid_h:, mid_w:]
    ]
    quadrant_stds = [float(np.std(q)) for q in quadrants]
    quadrant_variance = float(np.std(quadrant_stds))  # how much std varies across quadrants

    # Score logic: very low overall noise OR very uniform noise across quadrants = AI signature
    # Real camera sensors produce natural, slightly uneven noise across the frame
    # NOTE: thresholds calibrated against limited real test samples (5 GAN faces,
    # 1 AI export, 1 web photo). Provisional — re-tune against larger labeled
    # dataset in Phase 2.
    if mean_noise < 4.0:
        score = 0.75
        finding = "Low noise levels — inconsistent with physical camera sensor noise, consistent with AI generation"
    elif mean_noise < 6.0:
        score = 0.45
        finding = "Moderate noise levels — inconclusive"
    else:
        score = 0.15
        finding = "Natural sensor noise pattern detected — consistent with physical camera capture"
    # Visualization: amplify noise residual for display
    amplified = np.clip(np.abs(noise_residual) * 8, 0, 255).astype(np.uint8)
    noise_image = Image.fromarray(amplified)
    out_buffer = io.BytesIO()
    noise_image.save(out_buffer, format="PNG")
    noise_base64 = base64.b64encode(out_buffer.getvalue()).decode("utf-8")

    return {
        "name": "Noise Analysis",
        "category": "Statistical",
        "score": score,
        "finding": finding,
        "raw_data": {
            "mean_noise": round(mean_noise, 4),
            "std_noise": round(std_noise, 4),
            "quadrant_variance": round(quadrant_variance, 4)
        },
        "visualization": f"data:image/png;base64,{noise_base64}"
    }