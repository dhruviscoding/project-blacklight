import torch
from transformers import ViTForImageClassification, ViTImageProcessor
from PIL import Image

_model = None
_processor = None

MODEL_NAME = "prithivMLmods/Deep-Fake-Detector-v2-Model"


def load_model():
    global _model, _processor
    if _model is not None:
        return _model, _processor

    try:
        model = ViTForImageClassification.from_pretrained(MODEL_NAME)
        processor = ViTImageProcessor.from_pretrained(MODEL_NAME)
        model.eval()
        _model = model
        _processor = processor
        return _model, _processor
    except Exception as e:
        print(f"Failed to load modern classifier: {e}")
        return None, None


def analyze_modern_cnn(file_path):
    model, processor = load_model()

    if model is None:
        return {
            "name": "Modern AI Classifier",
            "category": "ML",
            "score": None,
            "finding": "Modern classifier unavailable - model failed to load",
            "raw_data": None
        }

    try:
        image = Image.open(file_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=1).squeeze().tolist()
            predicted_class = torch.argmax(logits, dim=1).item()

        label = model.config.id2label[predicted_class]
        label_map = {v.lower(): k for k, v in model.config.id2label.items()}
        fake_idx = label_map.get("fake", label_map.get("deepfake", 0))
        ai_probability = probs[fake_idx]

        if ai_probability > 0.7:
            finding = "Modern classifier strongly indicates AI generation"
        elif ai_probability > 0.4:
            finding = "Modern classifier shows moderate AI-generation signal"
        else:
            finding = "Modern classifier indicates likely authentic image"

        return {
            "name": "Modern AI Classifier",
            "category": "ML",
            "score": round(ai_probability, 4),
            "finding": finding,
            "raw_data": {"raw_probability": ai_probability, "predicted_label": label, "all_probs": probs}
        }
    except Exception as e:
        return {
            "name": "Modern AI Classifier",
            "category": "ML",
            "score": None,
            "finding": "Modern classifier failed: " + str(e),
            "raw_data": None
        }