from PIL import Image
import imagehash


def generate_perceptual_hashes(file_path: str) -> dict:
    """
    Generates perceptual hashes (pHash, dHash, aHash) for an image.
    Unlike cryptographic hashes, these allow detecting visually similar
    images even after resizing, compression, or minor edits.
    """
    image = Image.open(file_path)

    return {
        "phash": str(imagehash.phash(image)),
        "dhash": str(imagehash.dhash(image)),
        "ahash": str(imagehash.average_hash(image))
    }