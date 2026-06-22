import urllib.parse


def generate_reverse_search_links(image_url: str) -> dict:
    """
    Generates direct reverse-image-search links for major engines.
    No free programmatic API exists for reverse image search (TinEye's
    API starts at $200/5000 searches, Google/Bing have no free image
    search API). This provides one-click manual verification links
    for the investigator instead — free, no scraping, no ToS issues.

    image_url must be a publicly accessible URL to the uploaded image
    (e.g. a temporary signed URL from storage), since these search
    engines require a URL, not a raw file upload, for this method.
    """
    encoded_url = urllib.parse.quote(image_url, safe="")

    return {
        "name": "Reverse Image Search",
        "category": "Investigative",
        "score": None,  # informational only, does not feed verdict engine
        "finding": "Manual reverse search links generated — click to verify image origin across engines",
        "links": {
            "google_lens": f"https://lens.google.com/uploadbyurl?url={encoded_url}",
            "yandex": f"https://yandex.com/images/search?rpt=imageview&url={encoded_url}",
            "tineye": f"https://tineye.com/search?url={encoded_url}",
            "bing": f"https://www.bing.com/images/search?view=detailv2&iss=sbi&form=SBIIRP&q=imgurl:{encoded_url}"
        },
        "note": "Automated programmatic reverse search requires a paid API (e.g. TinEye, $200/5000 searches). Deferred to Phase 2/3."
    }