import librosa
import numpy as np


def detect_edit_artifacts(file_path: str) -> dict:
    """
    Detects signs of audio editing — splice points, sudden level discontinuities,
    unnatural level jumps, and abrupt spectral changes. These are forensic
    indicators of tampering regardless of whether AI was involved.
    """
    try:
        y, sr = librosa.load(file_path, sr=None, mono=True)
        duration = len(y) / sr

        if duration < 1.0:
            return {
                "edit_artifacts_detected": False,
                "findings": ["Audio too short for edit detection"],
                "splice_points": [],
                "level_discontinuities": []
            }

        # ---- Level Discontinuity Detection ----
        frame_length = int(sr * 0.05)  # 50ms frames
        hop_length = int(sr * 0.025)   # 25ms hop
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

        rms_diff = np.abs(np.diff(rms))
        rms_threshold = float(np.mean(rms_diff) + 3 * np.std(rms_diff))
        discontinuity_frames = np.where(rms_diff > rms_threshold)[0]

        discontinuity_times = [
            round(float(f * hop_length / sr), 3)
            for f in discontinuity_frames
        ]

        # ---- Spectral Discontinuity Detection (potential splice points) ----
        hop = int(sr * 0.010)
        stft = np.abs(librosa.stft(y, hop_length=hop))
        spectral_diff = np.mean(np.abs(np.diff(stft, axis=1)), axis=0)

        spec_threshold = float(np.mean(spectral_diff) + 3.5 * np.std(spectral_diff))
        splice_frames = np.where(spectral_diff > spec_threshold)[0]

        # Only flag if spectral AND level discontinuities are near each other
        # (reduces false positives from natural speech transitions)
        confirmed_splices = []
        for sf in splice_frames:
            sf_time = sf * hop / sr
            for df_time in discontinuity_times:
                if abs(sf_time - df_time) < 0.1:  # within 100ms
                    confirmed_splices.append(round(float(sf_time), 3))
                    break

        confirmed_splices = sorted(list(set(confirmed_splices)))

        # ---- DC Offset Check ----
        dc_offset = float(np.mean(y))
        dc_offset_flag = abs(dc_offset) > 0.01

        # ---- Clipping Detection ----
        clipping_ratio = float(np.mean(np.abs(y) > 0.99))
        clipping_flag = clipping_ratio > 0.001

        findings = []
        if confirmed_splices:
            findings.append(f"Potential splice/edit points detected at: {confirmed_splices[:5]} seconds")
        if len(discontinuity_times) > 5:
            findings.append(f"{len(discontinuity_times)} sudden level changes detected — possible editing")
        if dc_offset_flag:
            findings.append(f"DC offset detected ({dc_offset:.4f}) — may indicate processing artifacts")
        if clipping_flag:
            findings.append(f"Audio clipping detected ({clipping_ratio*100:.2f}% of samples) — possible compression or normalization")
        if not findings:
            findings.append("No significant editing artifacts detected")

        return {
            "edit_artifacts_detected": len(confirmed_splices) > 0 or len(discontinuity_times) > 5,
            "findings": findings,
            "splice_points": confirmed_splices[:10],
            "level_discontinuities": discontinuity_times[:10],
            "dc_offset": round(dc_offset, 6),
            "clipping_ratio": round(clipping_ratio, 6)
        }

    except Exception as e:
        return {"error": str(e), "edit_artifacts_detected": False, "findings": [str(e)]}