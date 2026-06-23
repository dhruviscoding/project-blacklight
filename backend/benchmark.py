import os
import json
import time
import requests
from pathlib import Path

BACKEND_URL = "http://127.0.0.1:8000"
AI_IMAGES_DIR = "benchmark/ai"
REAL_IMAGES_DIR = "benchmark/real"
RESULTS_FILE = "benchmark/results.json"


def analyze_image(file_path: str) -> dict:
    with open(file_path, "rb") as f:
        ext = Path(file_path).suffix.lower()
        mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png" if ext == ".png" else "image/webp"
        response = requests.post(
            f"{BACKEND_URL}/analyze/image",
            files={"file": (Path(file_path).name, f, mime)},
            timeout=120
        )
    return response.json()


def run_benchmark():
    os.makedirs("benchmark/ai", exist_ok=True)
    os.makedirs("benchmark/real", exist_ok=True)

    ai_images = list(Path(AI_IMAGES_DIR).glob("*.jpg")) + \
                list(Path(AI_IMAGES_DIR).glob("*.jpeg")) + \
                list(Path(AI_IMAGES_DIR).glob("*.png"))

    real_images = list(Path(REAL_IMAGES_DIR).glob("*.jpg")) + \
                  list(Path(REAL_IMAGES_DIR).glob("*.jpeg")) + \
                  list(Path(REAL_IMAGES_DIR).glob("*.png"))

    print(f"Found {len(ai_images)} AI images, {len(real_images)} real images")

    if len(ai_images) == 0 or len(real_images) == 0:
        print("ERROR: No images found. Add images to benchmark/ai/ and benchmark/real/ folders.")
        return

    results = {"ai": [], "real": [], "summary": {}}

    print("\nAnalyzing AI images...")
    for i, img_path in enumerate(ai_images[:100]):
        print(f"  [{i+1}/{min(len(ai_images), 100)}] {img_path.name}", end=" ")
        try:
            result = analyze_image(str(img_path))
            verdict = result.get("verdict", {}).get("verdict", "FAILED")
            confidence = result.get("verdict", {}).get("confidence", 0)
            results["ai"].append({
                "file": img_path.name,
                "verdict": verdict,
                "confidence": confidence,
                "correct": verdict not in ["LIKELY AUTHENTIC", "AUTHENTIC (CONFIRMED)"]
            })
            print(f"→ {verdict} ({confidence:.0%})")
        except Exception as e:
            print(f"→ ERROR: {e}")
            results["ai"].append({"file": img_path.name, "verdict": "ERROR", "confidence": 0, "correct": False})
        time.sleep(0.5)

    print("\nAnalyzing real images...")
    for i, img_path in enumerate(real_images[:100]):
        print(f"  [{i+1}/{min(len(real_images), 100)}] {img_path.name}", end=" ")
        try:
            result = analyze_image(str(img_path))
            verdict = result.get("verdict", {}).get("verdict", "FAILED")
            confidence = result.get("verdict", {}).get("confidence", 0)
            results["real"].append({
                "file": img_path.name,
                "verdict": verdict,
                "confidence": confidence,
                "correct": verdict not in ["AI GENERATED", "AI GENERATED (CONFIRMED)", "LIKELY AI GENERATED"]
            })
            print(f"→ {verdict} ({confidence:.0%})")
        except Exception as e:
            print(f"→ ERROR: {e}")
            results["real"].append({"file": img_path.name, "verdict": "ERROR", "confidence": 0, "correct": True})
        time.sleep(0.5)

    # Summary stats
    ai_correct = sum(1 for r in results["ai"] if r["correct"])
    real_correct = sum(1 for r in results["real"] if r["correct"])
    ai_total = len(results["ai"])
    real_total = len(results["real"])

    ai_verdicts = {}
    for r in results["ai"]:
        ai_verdicts[r["verdict"]] = ai_verdicts.get(r["verdict"], 0) + 1

    real_verdicts = {}
    for r in results["real"]:
        real_verdicts[r["verdict"]] = real_verdicts.get(r["verdict"], 0) + 1

    results["summary"] = {
        "ai_accuracy": ai_correct / ai_total if ai_total > 0 else 0,
        "real_accuracy": real_correct / real_total if real_total > 0 else 0,
        "overall_accuracy": (ai_correct + real_correct) / (ai_total + real_total) if (ai_total + real_total) > 0 else 0,
        "ai_verdict_distribution": ai_verdicts,
        "real_verdict_distribution": real_verdicts,
        "total_images": ai_total + real_total
    }

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*50}")
    print(f"BENCHMARK RESULTS")
    print(f"{'='*50}")
    print(f"AI images:   {ai_correct}/{ai_total} correct ({results['summary']['ai_accuracy']:.1%})")
    print(f"Real images: {real_correct}/{real_total} correct ({results['summary']['real_accuracy']:.1%})")
    print(f"Overall:     {ai_correct + real_correct}/{ai_total + real_total} ({results['summary']['overall_accuracy']:.1%})")
    print(f"\nAI verdict distribution: {ai_verdicts}")
    print(f"Real verdict distribution: {real_verdicts}")
    print(f"\nFull results saved to {RESULTS_FILE}")


if __name__ == "__main__":
    run_benchmark()