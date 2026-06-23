import librosa
import numpy as np


def analyze_audio_spectral(file_path: str) -> dict:
    """
    Enhanced spectral and prosodic analysis for forensic audio investigation.
    Extracts MFCC, pitch contour, harmonic-to-noise ratio, spectral flatness,
    and silence patterns. These signals serve both as forensic indicators
    (editing artifacts, voice consistency) and synthesis likelihood signals.
    """
    try:
        y, sr = librosa.load(file_path, sr=None, mono=True)
        duration = len(y) / sr

        # ---- MFCC Analysis ----
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = mfccs.mean(axis=1).tolist()
        mfcc_std = mfccs.std(axis=1).tolist()
        mfcc_delta_std = float(np.std(np.diff(mfccs, axis=1)))

        # ---- Pitch Contour Analysis ----
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            sr=sr
        )
        voiced_f0 = f0[voiced_flag] if f0 is not None else np.array([])

        if len(voiced_f0) > 10:
            pitch_mean = float(np.nanmean(voiced_f0))
            pitch_std = float(np.nanstd(voiced_f0))
            pitch_range = float(np.nanmax(voiced_f0) - np.nanmin(voiced_f0))
            voiced_ratio = float(np.sum(voiced_flag) / len(voiced_flag))
            # Unnaturally low std relative to mean suggests TTS pitch flattening
            pitch_flatness = pitch_std / (pitch_mean + 1e-6)
        else:
            pitch_mean = pitch_std = pitch_range = voiced_ratio = pitch_flatness = None

        # ---- Harmonic-to-Noise Ratio ----
        # Real voices have characteristic harmonic structure
        harmonic, percussive = librosa.effects.hpss(y)
        harmonic_energy = float(np.mean(harmonic ** 2))
        noise_energy = float(np.mean((y - harmonic) ** 2))
        hnr = float(10 * np.log10(harmonic_energy / (noise_energy + 1e-10)))

        # ---- Spectral Flatness ----
        # Measures how "noise-like" vs "tone-like" the spectrum is
        spectral_flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))

        # ---- Silence/Pause Pattern Analysis ----
        frame_length = int(sr * 0.025)
        hop_length = int(sr * 0.010)
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        silence_threshold = float(np.percentile(rms, 10))
        silence_frames = rms < silence_threshold
        silence_ratio = float(np.mean(silence_frames))

        # Detect pause patterns — look for silence gaps
        silence_changes = np.diff(silence_frames.astype(int))
        pause_starts = np.where(silence_changes == 1)[0]
        pause_ends = np.where(silence_changes == -1)[0]
        num_pauses = min(len(pause_starts), len(pause_ends))

        # ---- Synthesis Likelihood Indicators ----
        synthesis_indicators = []

        if pitch_flatness is not None and pitch_flatness < 0.15:
            synthesis_indicators.append("Low pitch variation — consistent with TTS synthesis or monotone delivery")

        if silence_ratio < 0.02 and duration > 5:
            synthesis_indicators.append("Very low silence ratio — natural breathing pauses may be absent")

        if num_pauses < 2 and duration > 10:
            synthesis_indicators.append("Few or no natural pause patterns detected")

        if spectral_flatness > 0.1:
            synthesis_indicators.append("High spectral flatness — audio may lack natural harmonic structure")

        # HNR reported as metric only — not flagged as synthesis indicator
        # due to high overlap between compressed real speech and TTS
        return {
            "duration_seconds": round(duration, 2),
            "sample_rate": sr,
            "mfcc": {
                "mean": [round(v, 4) for v in mfcc_mean],
                "std": [round(v, 4) for v in mfcc_std],
                "temporal_variation": round(mfcc_delta_std, 4)
            },
            "pitch": {
                "mean_hz": round(pitch_mean, 2) if pitch_mean else None,
                "std_hz": round(pitch_std, 2) if pitch_std else None,
                "range_hz": round(pitch_range, 2) if pitch_range else None,
                "voiced_ratio": round(voiced_ratio, 4) if voiced_ratio else None,
                "flatness_index": round(pitch_flatness, 4) if pitch_flatness else None
            },
            "harmonic_to_noise_ratio_db": round(hnr, 2),
            "spectral_flatness": round(spectral_flatness, 6),
            "silence": {
                "silence_ratio": round(silence_ratio, 4),
                "num_pauses": num_pauses
            },
            "synthesis_indicators": synthesis_indicators
        }

    except Exception as e:
        return {"error": str(e)}