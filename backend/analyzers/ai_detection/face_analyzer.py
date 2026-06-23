import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "models", "face_landmarker.task")
MODEL_PATH = os.path.normpath(MODEL_PATH)

_landmarker = None


def load_landmarker():
    global _landmarker
    if _landmarker is not None:
        return _landmarker
    try:
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=3,
            min_face_detection_confidence=0.5
        )
        _landmarker = vision.FaceLandmarker.create_from_options(options)
        return _landmarker
    except Exception as e:
        print(f"Failed to load face landmarker: {e}")
        return None


def analyze_face(file_path: str) -> dict:
    """
    Detects faces and analyzes facial landmarks for anatomical inconsistencies.
    AI-generated faces often show subtle asymmetry anomalies or impossible
    facial geometry. Absence of faces is neutral/inconclusive.
    """
    landmarker = load_landmarker()

    if landmarker is None:
        return {
            "name": "Face Landmark Analysis",
            "category": "Semantic",
            "score": 0.5,
            "finding": "Face landmarker model unavailable — inconclusive",
            "raw_data": None
        }

    try:
        image = mp.Image.create_from_file(file_path)
        results = landmarker.detect(image)

        if not results.face_landmarks:
            return {
                "name": "Face Landmark Analysis",
                "category": "Semantic",
                "score": 0.5,
                "finding": "No faces detected in image — inconclusive",
                "raw_data": {"faces_detected": 0}
            }

        faces_detected = len(results.face_landmarks)
        anomaly_scores = []

        for face_landmarks in results.face_landmarks:
            landmarks = [(lm.x, lm.y, lm.z) for lm in face_landmarks]

            # Symmetry check — compare left/right eye distance to nose
            left_eye_x = np.mean([landmarks[33][0], landmarks[133][0]])
            right_eye_x = np.mean([landmarks[362][0], landmarks[263][0]])
            nose_x = landmarks[1][0]

            left_dist = abs(nose_x - left_eye_x)
            right_dist = abs(nose_x - right_eye_x)

            if left_dist > 0 and right_dist > 0:
                symmetry_ratio = min(left_dist, right_dist) / max(left_dist, right_dist)
            else:
                symmetry_ratio = 1.0

            if symmetry_ratio > 0.97 or symmetry_ratio < 0.6:
                anomaly_scores.append(0.65)
            else:
                anomaly_scores.append(0.2)

            # Eye aspect ratio consistency
            left_eye_top = landmarks[159][1]
            left_eye_bottom = landmarks[145][1]
            right_eye_top = landmarks[386][1]
            right_eye_bottom = landmarks[374][1]

            left_ear = abs(left_eye_top - left_eye_bottom)
            right_ear = abs(right_eye_top - right_eye_bottom)

            if left_ear > 0 and right_ear > 0:
                ear_ratio = min(left_ear, right_ear) / max(left_ear, right_ear)
                if ear_ratio < 0.5:
                    anomaly_scores.append(0.70)
                else:
                    anomaly_scores.append(0.15)

        avg_anomaly = sum(anomaly_scores) / len(anomaly_scores) if anomaly_scores else 0.5

        if avg_anomaly > 0.55:
            finding = f"Facial landmark anomalies detected across {faces_detected} face(s) — symmetry/geometry inconsistencies present"
        else:
            finding = f"{faces_detected} face(s) detected — landmarks appear anatomically consistent"

        return {
            "name": "Face Landmark Analysis",
            "category": "Semantic",
            "score": round(avg_anomaly, 4),
            "finding": finding,
            "raw_data": {
                "faces_detected": faces_detected,
                "avg_anomaly_score": round(avg_anomaly, 4),
                "anomaly_scores": [round(s, 4) for s in anomaly_scores]
            }
        }

    except Exception as e:
        return {
            "name": "Face Landmark Analysis",
            "category": "Semantic",
            "score": 0.5,
            "finding": f"Face analysis failed: {str(e)}",
            "raw_data": None
        }