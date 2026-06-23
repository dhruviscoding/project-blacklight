import librosa
import numpy as np
import torch

_model = None


def load_model():
    global _model
    if _model is not None:
        return _model
    try:
        from speechbrain.inference.speaker import EncoderClassifier
        _model = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="models/spkrec-ecapa-voxceleb"
        )
        return _model
    except Exception as e:
        print(f"Failed to load speaker model: {e}")
        return None


def analyze_speaker_consistency(file_path: str) -> dict:
    """
    Checks if the same speaker is present throughout the audio using
    ECAPA-TDNN speaker embeddings. Identity shifts mid-recording suggest
    splicing, voice swapping, or multiple speakers — forensically significant
    regardless of AI involvement.
    """
    model = load_model()

    if model is None:
        return {
            "name": "Speaker Consistency",
            "consistent": None,
            "finding": "Speaker model unavailable — inconclusive",
            "segments_analyzed": 0
        }

    try:
        y, sr = librosa.load(file_path, sr=16000, mono=True)
        duration = len(y) / sr

        if duration < 4.0:
            return {
                "name": "Speaker Consistency",
                "consistent": None,
                "finding": "Audio too short for speaker consistency analysis (minimum 4 seconds)",
                "segments_analyzed": 0
            }

        # Split into 2-second segments with 1-second overlap
        segment_length = 2 * sr
        hop = sr
        segments = []
        for start in range(0, len(y) - segment_length, hop):
            segments.append(y[start:start + segment_length])

        if len(segments) < 2:
            return {
                "name": "Speaker Consistency",
                "consistent": None,
                "finding": "Not enough segments for comparison",
                "segments_analyzed": len(segments)
            }

        # Extract embeddings for each segment
        embeddings = []
        for seg in segments[:20]:  # cap at 20 segments to avoid timeout
            seg_tensor = torch.tensor(seg).unsqueeze(0)
            with torch.no_grad():
                emb = model.encode_batch(seg_tensor)
            embeddings.append(emb.squeeze().numpy())

        embeddings = np.array(embeddings)

        # Compute cosine similarities between consecutive segments
        similarities = []
        for i in range(len(embeddings) - 1):
            a = embeddings[i]
            b = embeddings[i + 1]
            cos_sim = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))
            similarities.append(cos_sim)

        mean_similarity = float(np.mean(similarities))
        min_similarity = float(np.min(similarities))
        std_similarity = float(np.std(similarities))

        # Flag segments where similarity drops sharply
        low_similarity_threshold = mean_similarity - 2 * std_similarity
        identity_shifts = [
            round(i * 1.0, 1)
            for i, sim in enumerate(similarities)
            if sim < low_similarity_threshold and sim < 0.75
        ]

        if mean_similarity > 0.85 and not identity_shifts:
            consistent = True
            finding = f"Speaker consistent throughout recording (mean similarity: {mean_similarity:.2f})"
        elif identity_shifts:
            consistent = False
            finding = f"Possible speaker identity shifts detected at {identity_shifts} seconds — forensically significant"
        else:
            consistent = None
            finding = f"Speaker consistency uncertain (mean similarity: {mean_similarity:.2f}, min: {min_similarity:.2f})"

        return {
            "name": "Speaker Consistency",
            "consistent": consistent,
            "finding": finding,
            "segments_analyzed": len(segments),
            "mean_similarity": round(mean_similarity, 4),
            "min_similarity": round(min_similarity, 4),
            "identity_shift_timestamps": identity_shifts
        }

    except Exception as e:
        return {
            "name": "Speaker Consistency",
            "consistent": None,
            "finding": f"Speaker analysis failed: {str(e)}",
            "segments_analyzed": 0
        }