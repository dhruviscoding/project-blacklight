import torch
import torch.nn as nn
from torchvision.models import resnet50
from torchvision import transforms
from PIL import Image

MODEL_PATH = "models/cnndetection.pth"

_model = None


def load_model():
    """
    Loads the CNNDetection pretrained model once at startup.
    Returns None if loading fails, so the verdict engine can
    gracefully exclude this signal instead of crashing.
    """
    global _model
    if _model is not None:
        return _model

    try:
        model = resnet50(num_classes=1)
        state_dict = torch.load(MODEL_PATH, map_location="cpu")
        model.load_state_dict(state_dict["model"])
        model.eval()
        _model = model
        return _model
    except Exception as e:
        print(f"Failed to load CNN classifier: {e}")
        return None


_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def analyze_cnn(file_path: str) -> dict:
    """
    Runs the CNNDetection classifier on an image.
    Returns AI-generation probability based on a model trained to
    distinguish real photos from CNN/GAN-generated images.
    """
    model = load_model()

    if model is None:
        return {
            "name": "CNN Classifier",
            "category": "ML",
            "score": None,
            "finding": "CNN classifier unavailable — model failed to load",
            "raw_data": None
        }

    try:
        image = Image.open(file_path).convert("RGB")
        tensor = _transform(image).unsqueeze(0)

        with torch.no_grad():
            output = model(tensor)
            probability = torch.sigmoid(output).item()

        if probability > 0.7:
            finding = f"CNN classifier strongly indicates AI/GAN generation ({probability*100:.1f}% probability)"
        elif probability > 0.4:
            finding = f"CNN classifier shows moderate AI-generation signal ({probability*100:.1f}% probability)"
        else:
            finding = f"CNN classifier indicates likely authentic image ({probability*100:.1f}% AI probability)"

        return {
            "name": "CNN Classifier",
            "category": "ML",
            "score": round(probability, 4),
            "finding": finding,
            "raw_data": {"raw_probability": probability}
        }
    except Exception as e:
        return {
            "name": "CNN Classifier",
            "category": "ML",
            "score": None,
            "finding": f"CNN classifier failed: {str(e)}",
            "raw_data": None
        }