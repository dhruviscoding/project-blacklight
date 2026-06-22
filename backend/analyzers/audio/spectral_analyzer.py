import librosa
import numpy as np


def analyze_audio_spectral(file_path: str) -> dict:
    """
    Basic spectral analysis of audio files using librosa.
    Returns spectral statistics that serve as preliminary indicators.
    Full AI voice detection (resemblyzer, speechbrain) deferred to Phase 2.
    """
    try:
        y, sr = librosa.load(file_path, sr=None, mono=True)

        # Basic spectral features
        spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
        spectral_rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
        zero_crossing_rate = float(np.mean(librosa.feature.zero_crossing_rate(y)))

        # Silence ratio — AI voices often have unnaturally low silence
        silence_threshold = 0.01
        silence_ratio = float(np.mean(np.abs(y) < silence_threshold))

        # RMS energy
        rms = float(np.mean(librosa.feature.rms(y=y)))

        return {
            "spectral_centroid": round(spectral_centroid, 2),
            "spectral_rolloff": round(spectral_rolloff, 2),
            "zero_crossing_rate": round(zero_crossing_rate, 4),
            "silence_ratio": round(silence_ratio, 4),
            "rms_energy": round(rms, 4),
            "duration_seconds": round(len(y) / sr, 2),
            "sample_rate": sr
        }
    except Exception as e:
        return {"error": str(e)}