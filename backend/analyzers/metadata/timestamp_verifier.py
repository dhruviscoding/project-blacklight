from datetime import datetime


def verify_timestamps(raw_metadata: dict) -> dict:
    """
    Compares various timestamp fields to detect inconsistencies
    that may indicate tampering or AI generation.
    """
    date_original = raw_metadata.get("EXIF:DateTimeOriginal")
    date_digitized = raw_metadata.get("EXIF:CreateDate")
    file_modify_date = raw_metadata.get("File:FileModifyDate")
    file_create_date = raw_metadata.get("File:FileCreateDate")

    findings = []
    inconsistent = False

    def parse_exif_date(date_str):
        if not date_str:
            return None
        try:
            # ExifTool format: "2026:06:19 16:15:52+05:30"
            clean = date_str.split("+")[0].split("-")[0].strip()
            return datetime.strptime(clean, "%Y:%m:%d %H:%M:%S")
        except (ValueError, IndexError):
            return None

    original_dt = parse_exif_date(date_original)
    digitized_dt = parse_exif_date(date_digitized)
    modify_dt = parse_exif_date(file_modify_date)
    create_dt = parse_exif_date(file_create_date)

    if original_dt is None and digitized_dt is None:
        findings.append("No original capture timestamp found in metadata — inconclusive (normal for downloaded/shared images)")
        # Do NOT flag as inconsistent — missing timestamps are normal for web/social images
    if original_dt and modify_dt:
        delta = abs((modify_dt - original_dt).total_seconds())
        # If file was modified more than 1 hour after the claimed capture time
        if delta > 3600:
            findings.append(f"File modification date differs from capture date by {delta/3600:.1f} hours")
            inconsistent = True

    if original_dt and digitized_dt and original_dt != digitized_dt:
        findings.append("DateTimeOriginal and CreateDate fields do not match")
        inconsistent = True

    return {
        "date_original": date_original,
        "date_digitized": date_digitized,
        "file_modify_date": file_modify_date,
        "file_create_date": file_create_date,
        "inconsistent": inconsistent,
        "findings": findings if findings else ["Timestamps appear consistent"]
    }