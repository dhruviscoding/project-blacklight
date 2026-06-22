import mutagen


def analyze_audio_metadata(file_path: str) -> dict:
    """
    Extracts metadata from audio files using mutagen.
    Returns codec, encoder, creation tool, duration, sample rate, bitrate.
    """
    try:
        audio = mutagen.File(file_path, easy=True)

        if audio is None:
            return {
                "error": "Could not read audio file",
                "format": None,
                "duration": None,
                "bitrate": None,
                "sample_rate": None,
                "tags": {}
            }

        info = audio.info if hasattr(audio, 'info') else None

        return {
            "format": type(audio).__name__,
            "duration": round(info.length, 2) if info and hasattr(info, 'length') else None,
            "bitrate": info.bitrate if info and hasattr(info, 'bitrate') else None,
            "sample_rate": info.sample_rate if info and hasattr(info, 'sample_rate') else None,
            "channels": info.channels if info and hasattr(info, 'channels') else None,
            "tags": dict(audio.tags) if audio.tags else {}
        }
    except Exception as e:
        return {"error": str(e)}