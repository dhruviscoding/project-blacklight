import ffmpeg


def analyze_video_metadata(file_path: str) -> dict:
    """
    Extracts container metadata from video files using ffmpeg-python.
    Returns codec, encoder, creation time, duration, resolution, framerate.
    """
    try:
        probe = ffmpeg.probe(file_path)
        format_info = probe.get("format", {})
        streams = probe.get("streams", [])

        video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

        tags = format_info.get("tags", {})

        return {
            "format": format_info.get("format_long_name"),
            "duration": round(float(format_info.get("duration", 0)), 2),
            "size_bytes": int(format_info.get("size", 0)),
            "bit_rate": int(format_info.get("bit_rate", 0)),
            "encoder": tags.get("encoder") or tags.get("ENCODER"),
            "creation_time": tags.get("creation_time"),
            "video_codec": video_stream.get("codec_name") if video_stream else None,
            "resolution": f"{video_stream.get('width')}x{video_stream.get('height')}" if video_stream else None,
            "frame_rate": video_stream.get("r_frame_rate") if video_stream else None,
            "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
            "audio_sample_rate": audio_stream.get("sample_rate") if audio_stream else None
        }
    except Exception as e:
        return {"error": str(e)}