import exiftool
from analyzers.metadata.gps_extractor import extract_gps
from analyzers.metadata.timestamp_verifier import verify_timestamps
from analyzers.metadata.tampering_detector import detect_tampering


def analyze_metadata(file_path: str) -> dict:
    """
    Extracts EXIF, IPTC, and XMP metadata from an image file.
    Returns a structured dict with all available metadata fields.
    """
    with exiftool.ExifToolHelper() as et:
        metadata_list = et.get_metadata(file_path)

    if not metadata_list:
        return {"error": "No metadata could be extracted"}

    raw_metadata = metadata_list[0]

    exif_data = {}
    iptc_data = {}
    xmp_data = {}
    other_data = {}

    for key, value in raw_metadata.items():
        if key.startswith("EXIF:"):
            exif_data[key.replace("EXIF:", "")] = value
        elif key.startswith("IPTC:"):
            iptc_data[key.replace("IPTC:", "")] = value
        elif key.startswith("XMP:"):
            xmp_data[key.replace("XMP:", "")] = value
        else:
            other_data[key] = value

    return {
        "exif": exif_data,
        "iptc": iptc_data,
        "xmp": xmp_data,
        "other": other_data,
        "raw": raw_metadata
    }


def get_full_metadata_signal(file_path: str) -> dict:
    """
    Runs the full metadata pipeline and returns a unified signal
    ready for the verdict engine.
    """
    metadata_result = analyze_metadata(file_path)

    if "error" in metadata_result:
        return {
            "name": "Metadata Analysis",
            "category": "Metadata",
            "score": 0.0,
            "finding": "Metadata extraction failed",
            "raw_data": None
        }

    raw = metadata_result["raw"]

    gps = extract_gps(raw)
    timestamps = verify_timestamps(raw)
    tampering = detect_tampering(raw)

    final_score = tampering["score"]
    if timestamps["inconsistent"]:
        final_score = min(1.0, final_score + 0.2)

    all_findings = tampering["findings"] + timestamps["findings"]

    return {
        "name": "Metadata Analysis",
        "category": "Metadata",
        "score": round(final_score, 2),
        "finding": "; ".join(all_findings),
        "raw_data": {
            "exif": metadata_result["exif"],
            "iptc": metadata_result["iptc"],
            "xmp": metadata_result["xmp"],
            "gps": gps,
            "timestamps": timestamps,
            "tampering": tampering
        }
    }