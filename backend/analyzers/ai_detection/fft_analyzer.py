from PIL import Image
import numpy as np
import io
import base64


def analyze_fft(file_path: str) -> dict:
    """
    Performs FFT (Fast Fourier Transform) frequency domain analysis.
    GAN-based generators often leave periodic high-frequency artifacts
    (checkerboard patterns) from their upsampling layers, invisible in
    the spatial domain but detectable in the frequency domain.
    """
    image = Image.open(file_path).convert("L")  # grayscale
    img_array = np.array(image, dtype=np.float64)

    # 2D FFT
    fft = np.fft.fft2(img_array)
    fft_shifted = np.fft.fftshift(fft)
    magnitude_spectrum = np.log(np.abs(fft_shifted) + 1)

    h, w = magnitude_spectrum.shape
    center_y, center_x = h // 2, w // 2

    # Define high-frequency region (outer ring of the spectrum)
    y, x = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    max_dist = np.sqrt(center_x**2 + center_y**2)

    high_freq_mask = dist_from_center > (max_dist * 0.7)
    high_freq_region = magnitude_spectrum[high_freq_mask]

    # Peak-to-average ratio in high-frequency band
    # GAN checkerboard artifacts create sharp periodic peaks here
    mean_high_freq = float(np.mean(high_freq_region))
    max_high_freq = float(np.max(high_freq_region))
    std_high_freq = float(np.std(high_freq_region))

    peak_to_avg_ratio = max_high_freq / (mean_high_freq + 1e-6)

    # Score logic: high peak-to-average ratio = periodic artifacts = GAN signature
    # NOTE: thresholds calibrated against limited real test samples (1 GAN, 1 web photo).
    # These are provisional — should be re-tuned against a larger labeled dataset in Phase 2.
    if peak_to_avg_ratio > 1.6:
        score = 0.8
        finding = "Strong periodic high-frequency artifacts detected — consistent with GAN upsampling signature"
    elif peak_to_avg_ratio > 1.4:
        score = 0.5
        finding = "Moderate high-frequency irregularities — inconclusive"
    else:
        score = 0.15
        finding = "Natural high-frequency distribution — no GAN-characteristic artifacts detected"
    # Normalize magnitude spectrum to 0-255 for visualization
    norm_spectrum = (magnitude_spectrum - magnitude_spectrum.min()) / (magnitude_spectrum.max() - magnitude_spectrum.min() + 1e-6)
    norm_spectrum = (norm_spectrum * 255).astype(np.uint8)

    fft_image = Image.fromarray(norm_spectrum)
    out_buffer = io.BytesIO()
    fft_image.save(out_buffer, format="PNG")
    fft_base64 = base64.b64encode(out_buffer.getvalue()).decode("utf-8")

    return {
        "name": "FFT Frequency Analysis",
        "category": "Statistical",
        "score": score,
        "finding": finding,
        "raw_data": {
            "mean_high_freq": round(mean_high_freq, 4),
            "max_high_freq": round(max_high_freq, 4),
            "peak_to_avg_ratio": round(peak_to_avg_ratio, 4)
        },
        "visualization": f"data:image/png;base64,{fft_base64}"
    }