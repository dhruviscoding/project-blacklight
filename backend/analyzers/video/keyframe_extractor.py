import ffmpeg
import os


def extract_keyframes(file_path: str, interval_seconds: int = 5) -> list:
    """
    Extracts one keyframe every N seconds from a video file using ffmpeg.
    Returns a list of paths to the extracted frame images.
    These frames are then run through the full image analysis pipeline.
    """
    try:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_dir = f"temp/frames_{base_name}"
        os.makedirs(output_dir, exist_ok=True)

        output_pattern = f"{output_dir}/frame_%04d.jpg"

        (
            ffmpeg
            .input(file_path)
            .filter("fps", fps=f"1/{interval_seconds}")
            .output(output_pattern, vsync="vfr", q=2)
            .overwrite_output()
            .run(quiet=True)
        )

        frames = sorted([
            os.path.join(output_dir, f)
            for f in os.listdir(output_dir)
            if f.endswith(".jpg")
        ])

        return frames

    except Exception as e:
        return []