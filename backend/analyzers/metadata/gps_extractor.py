def extract_gps(raw_metadata: dict) -> dict:
    """
    Extracts and converts GPS coordinates from raw EXIF metadata.
    Returns None for lat/lon if no GPS data is present.
    """
    lat = raw_metadata.get("EXIF:GPSLatitude")
    lon = raw_metadata.get("EXIF:GPSLongitude")
    lat_ref = raw_metadata.get("EXIF:GPSLatitudeRef")
    lon_ref = raw_metadata.get("EXIF:GPSLongitudeRef")
    altitude = raw_metadata.get("EXIF:GPSAltitude")

    if lat is None or lon is None:
        return {
            "has_gps": False,
            "latitude": None,
            "longitude": None,
            "altitude": None
        }

    # ExifTool usually already returns decimal degrees, but handle ref sign correctly
    decimal_lat = float(lat)
    decimal_lon = float(lon)

    if lat_ref == "S":
        decimal_lat = -decimal_lat
    if lon_ref == "W":
        decimal_lon = -decimal_lon

    return {
        "has_gps": True,
        "latitude": decimal_lat,
        "longitude": decimal_lon,
        "altitude": float(altitude) if altitude else None
    }