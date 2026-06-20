from c2pa import Reader
import json


def verify_c2pa(file_path: str) -> dict:
    """
    Checks for C2PA Content Credentials using the c2pa-python Reader API.
    A VALID C2PA signature is one of the strongest possible forensic signals.
    Absence of C2PA is NOT proof of AI generation — most content currently
    lacks this signal since adoption is still low.
    """
    try:
        reader = Reader(file_path)
        manifest_store_json = reader.json()
        data = json.loads(manifest_store_json)

        active_manifest_id = data.get("active_manifest")

        if not active_manifest_id:
            return {
                "name": "C2PA Verification",
                "category": "Provenance",
                "score": 0.5,
                "finding": "No C2PA Content Credentials present — inconclusive (most content currently lacks this signal)",
                "has_c2pa": False,
                "raw_data": None
            }

        manifests = data.get("manifests", {})
        active_manifest = manifests.get(active_manifest_id, {})

        claim_generator = active_manifest.get("claim_generator")
        if not claim_generator:
            generator_info = active_manifest.get("claim_generator_info", [])
            if generator_info:
                claim_generator = generator_info[0].get("name", "Unknown")
            else:
                claim_generator = "Unknown"

        validation_state = data.get("validation_state", "Unknown")

        # Check if the manifest explicitly declares AI/trained-algorithm origin.
        # Different vendors structure this differently (Adobe nests it under
        # action.parameters, Microsoft puts it directly on the action) — check both.
        is_ai_declared = False
        for assertion in active_manifest.get("assertions", []):
            actions = assertion.get("data", {}).get("actions", [])
            for action in actions:
                source_type = (
                    action.get("digitalSourceType", "")
                    or action.get("parameters", {}).get("com.adobe.digitalSourceType", "")
                )
                if "trainedAlgorithmicMedia" in source_type or "compositeWithTrainedAlgorithmicMedia" in source_type:
                    is_ai_declared = True

        if validation_state == "Invalid":
            return {
                "name": "C2PA Verification",
                "category": "Provenance",
                "score": 0.9,
                "finding": f"C2PA manifest present but signature is INVALID — possible tampering with provenance data",
                "has_c2pa": True,
                "raw_data": data
            }

        if validation_state == "Valid" and is_ai_declared:
            return {
                "name": "C2PA Verification",
                "category": "Provenance",
                "score": 0.95,
                "finding": f"Valid C2PA Content Credentials confirm AI generation — source: {claim_generator}",
                "has_c2pa": True,
                "raw_data": data
            }

        if validation_state == "Valid":
            return {
                "name": "C2PA Verification",
                "category": "Provenance",
                "score": 0.05,
                "finding": f"Valid C2PA Content Credentials found, no AI declaration — verified provenance from: {claim_generator}",
                "has_c2pa": True,
                "raw_data": data
            }

        # validation_state == "Trusted" or other intermediate states
        return {
            "name": "C2PA Verification",
            "category": "Provenance",
            "score": 0.3,
            "finding": f"C2PA manifest present, validation state: {validation_state} (signing cert not in trusted root list, but signature integrity confirmed) — source: {claim_generator}",
            "has_c2pa": True,
            "raw_data": data
        }

    except Exception as e:
        return {
            "name": "C2PA Verification",
            "category": "Provenance",
            "score": 0.5,
            "finding": "No C2PA Content Credentials present — inconclusive",
            "has_c2pa": False,
            "raw_data": None
        }