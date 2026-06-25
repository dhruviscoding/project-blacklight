import pytesseract
from PIL import Image
import re

import os
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH", "tesseract")


def analyze_ocr(file_path: str) -> dict:
    """
    Runs OCR on the image and checks for AI-generation text artifacts.
    AI generators frequently produce garbled, nonsensical, or impossible text
    (wrong letter combinations, mixed scripts, pseudo-words) — a known weakness
    of current diffusion models. Absence of text is neutral/inconclusive.
    """
    try:
        image = Image.open(file_path).convert("RGB")
        text = pytesseract.image_to_string(image, config="--psm 3")
        text = text.strip()

        if not text or len(text) < 5:
            return {
                "name": "OCR Text Analysis",
                "category": "Semantic",
                "score": 0.5,
                "finding": "No significant text detected in image — inconclusive",
                "raw_data": {"text": "", "word_count": 0}
            }

        words = text.split()
        word_count = len(words)

        # Check for garbled text patterns common in AI-generated images
        garbled_count = 0
        for word in words:
            clean = re.sub(r'[^a-zA-Z]', '', word)
            if len(clean) < 2:
                continue
            # Flag words with unusual consonant clusters or random character sequences
            consonant_cluster = re.search(r'[bcdfghjklmnpqrstvwxyz]{4,}', clean.lower())
            # Flag words that look like random character strings
            no_vowel = not re.search(r'[aeiou]', clean.lower()) and len(clean) > 3
            if consonant_cluster or no_vowel:
                garbled_count += 1

        garbled_ratio = garbled_count / max(word_count, 1)

        if garbled_ratio > 0.4:
            score = 0.80
            finding = f"High proportion of garbled/nonsensical text detected ({garbled_count}/{word_count} words) — consistent with AI text generation artifacts"
        elif garbled_ratio > 0.2:
            score = 0.55
            finding = f"Some garbled text detected ({garbled_count}/{word_count} words) — inconclusive"
        else:
            score = 0.15
            finding = f"Text appears coherent ({word_count} words detected) — no AI text artifacts found"

        return {
            "name": "OCR Text Analysis",
            "category": "Semantic",
            "score": score,
            "finding": finding,
            "raw_data": {
                "text": text[:500],  # cap at 500 chars for response size
                "word_count": word_count,
                "garbled_count": garbled_count,
                "garbled_ratio": round(garbled_ratio, 3)
            }
        }

    except Exception as e:
        return {
            "name": "OCR Text Analysis",
            "category": "Semantic",
            "score": 0.5,
            "finding": f"OCR analysis failed: {str(e)}",
            "raw_data": None
        }