def run_verdict_engine(signals: dict) -> dict:
    """
    Weighted evidence fusion engine for AI-generated image detection.
 
    Signal weights (research-backed):
    - ML ensemble (ViT 70% + CNN 30%): 0.40 total
    - Noise Analysis: 0.30
    - FFT Analysis: 0.15
    - Metadata Analysis: 0.10
    - ELA: 0.05
 
    Special logic:
    - C2PA: priority override if decisive
    - Conflict detection: operates at category level (ML vs Statistical vs Provenance)
      CNN vs ViT disagreement is NOT a conflict — it's an internal uncertainty metric
    - Coverage penalty: caps confidence if fewer than 3 signals available
    - Cross-signal coherence: slight bonus if all categories agree
    """
 
    # ----------------------------------------------------------------
    # Step 1 — Extract individual signal scores
    # ----------------------------------------------------------------
    c2pa = signals.get("c2pa")
    cnn = signals.get("cnn")
    vit = signals.get("vit")
    fft = signals.get("fft")
    noise = signals.get("noise")
    metadata = signals.get("metadata")
    ela = signals.get("ela")
    ocr = signals.get("ocr")
    face = signals.get("face")

    all_signals = {
        "C2PA Verification": c2pa,
        "CNN Classifier": cnn,
        "Modern AI Classifier": vit,
        "FFT Frequency Analysis": fft,
        "Noise Analysis": noise,
        "Metadata Analysis": metadata,
        "Error Level Analysis": ela,
        "OCR Text Analysis": ocr,
        "Face Landmark Analysis": face
    }
 
    # ----------------------------------------------------------------
    # Step 2 — C2PA priority override
    # ----------------------------------------------------------------
    if c2pa is not None:
        if c2pa.get("score") == 0.95:
            return _build_verdict(
                verdict="AI GENERATED (CONFIRMED)",
                confidence=0.95,
                risk="CRITICAL",
                decisive_signal="C2PA Verification",
                conflict=False,
                coverage_warning=False,
                ml_agreement="N/A",
                signals=all_signals,
                summary="C2PA Content Credentials cryptographically confirm AI generation. This overrides probabilistic signals."
            )
        if c2pa.get("score") == 0.05:
            return _build_verdict(
                verdict="AUTHENTIC (CONFIRMED)",
                confidence=0.95,
                risk="LOW",
                decisive_signal="C2PA Verification",
                conflict=False,
                coverage_warning=False,
                ml_agreement="N/A",
                signals=all_signals,
                summary="C2PA Content Credentials cryptographically confirm authentic origin. This overrides probabilistic signals."
            )
 
    # ----------------------------------------------------------------
    # Step 3 — ML ensemble (ViT 70% + CNN 30%)
    # CNN vs ViT disagreement is an internal uncertainty metric only,
    # NOT a verdict-level conflict. Users don't care which neural net
    # disagreed with which — they care if ML disagrees with forensic signals.
    # ----------------------------------------------------------------
    cnn_score = cnn["score"] if cnn and cnn["score"] is not None else None
    vit_score = vit["score"] if vit and vit["score"] is not None else None
 
    if cnn_score is not None and vit_score is not None:
        combined_ml = (vit_score * 0.70) + (cnn_score * 0.30)
        ml_agreement_value = 1.0 - abs(cnn_score - vit_score)
        ml_agreement = "High" if ml_agreement_value > 0.7 else "Medium" if ml_agreement_value > 0.4 else "Low"
    elif vit_score is not None:
        combined_ml = vit_score
        ml_agreement = "Single model (ViT only)"
    elif cnn_score is not None:
        combined_ml = cnn_score
        ml_agreement = "Single model (CNN only)"
    else:
        combined_ml = None
        ml_agreement = "Unavailable"
 
    # ----------------------------------------------------------------
    # Step 4 — Build weighted signal pool with dynamic reweighting
    # ----------------------------------------------------------------
    fft_score = fft["score"] if fft and fft["score"] is not None else None
    noise_score = noise["score"] if noise and noise["score"] is not None else None
    metadata_score = metadata["score"] if metadata and metadata["score"] is not None else None
    ela_score = ela["score"] if ela and ela["score"] is not None else None
 
    ocr_score = ocr["score"] if ocr and ocr["score"] is not None else None
    face_score = face["score"] if face and face["score"] is not None else None

    # Semantic signals (OCR, face) are neutral at 0.5 — only contribute when
    # they find something meaningful (garbled text, facial anomalies)
    # Don't include neutral 0.5 scores in weighted average — too noisy
    ocr_weighted = ocr_score if ocr_score is not None and ocr_score != 0.5 else None
    face_weighted = face_score if face_score is not None and face_score != 0.5 else None

    base_weights = {
        "ml": (combined_ml, 0.38),
        "noise": (noise_score, 0.28),
        "fft": (fft_score, 0.14),
        "metadata": (metadata_score, 0.10),
        "ela": (ela_score, 0.05),
        "ocr": (ocr_weighted, 0.03),
        "face": (face_weighted, 0.02),
    }
 
    # Filter out None scores, redistribute weights proportionally
    available = {k: v for k, v in base_weights.items() if v[0] is not None}
    total_weight = sum(w for _, w in available.values())
    normalized = {k: (score, weight / total_weight) for k, (score, weight) in available.items()}
 
    # Coverage check
    coverage = len(available)
    coverage_warning = coverage < 3
 
    # ----------------------------------------------------------------
    # Step 5 — Category-level conflict detection
    # Conflict = meaningful disagreement between independent evidence categories:
    # ML category vs Statistical category vs Provenance category
    # ----------------------------------------------------------------
    ml_category = combined_ml
 
    statistical_scores = [s for s in [fft_score, noise_score, ela_score] if s is not None]
    statistical_category = sum(statistical_scores) / len(statistical_scores) if statistical_scores else None

    # Semantic signals only contribute to category scoring when non-neutral
    semantic_scores = [s for s in [ocr_score, face_score] if s is not None and s != 0.5]
    semantic_category = sum(semantic_scores) / len(semantic_scores) if semantic_scores else None
 
    provenance_category = metadata_score
 
    category_scores = [s for s in [ml_category, statistical_category, provenance_category, semantic_category] if s is not None]

    conflict_detected = False
    coherence_bonus = 0.0

    if len(category_scores) >= 2:
        mean_cat = sum(category_scores) / len(category_scores)
        variance = sum((s - mean_cat) ** 2 for s in category_scores) / len(category_scores)
        std_dev = variance ** 0.5

        # Conflict only when variance is genuinely high — one outlier against
        # strong consensus should not trigger INCONCLUSIVE.
        # std_dev > 0.25 means categories are meaningfully spread apart.
        # Simple max-min was too sensitive to single weak outliers (e.g. ViT
        # underperforming on StyleGAN while CNN+FFT+Noise strongly agree).
        if std_dev > 0.25:
            conflict_detected = True
        elif std_dev < 0.08:
            coherence_bonus = 0.05
 
    # ----------------------------------------------------------------
    # Step 6 — Weighted average
    # ----------------------------------------------------------------
    if not normalized:
        return _build_verdict(
            verdict="INCONCLUSIVE",
            confidence=0.0,
            risk="UNKNOWN",
            decisive_signal=None,
            conflict=False,
            coverage_warning=True,
            ml_agreement=ml_agreement,
            signals=all_signals,
            summary="No signals were available — analysis failed completely."
        )
 
    weighted_score = sum(score * weight for score, weight in normalized.values())
    weighted_score = min(1.0, weighted_score + coherence_bonus)
 
    # ----------------------------------------------------------------
    # Step 7 — Coverage confidence cap
    # ----------------------------------------------------------------
    confidence = weighted_score
    if coverage_warning:
        confidence = min(confidence, 0.65)
 
    # ----------------------------------------------------------------
    # Step 8 — Conflict override
    # ----------------------------------------------------------------
    if conflict_detected:
        return _build_verdict(
            verdict="INCONCLUSIVE — Conflicting signals, manual review recommended",
            confidence=confidence,
            risk="MEDIUM",
            decisive_signal=None,
            conflict=True,
            coverage_warning=coverage_warning,
            ml_agreement=ml_agreement,
            signals=all_signals,
            summary=f"Signals from different analysis categories disagree strongly. "
                    f"ML ensemble agreement: {ml_agreement}. "
                    f"Manual review by a trained forensic analyst is recommended."
        )
 
    # ----------------------------------------------------------------
    # Step 9 — Verdict thresholds
    # ----------------------------------------------------------------
    if confidence < 0.35:
        verdict = "LIKELY AUTHENTIC"
        risk = "LOW"
    elif confidence < 0.60:
        verdict = "INCONCLUSIVE"
        risk = "MEDIUM"
    elif confidence < 0.80:
        verdict = "LIKELY AI GENERATED"
        risk = "HIGH"
    else:
        verdict = "AI GENERATED"
        risk = "CRITICAL"
 
    top_signal = max(normalized.items(), key=lambda x: x[1][0] * x[1][1])
    summary = (
        f"{coverage} of 5 signal categories available. "
        f"Weighted confidence: {confidence:.0%}. "
        f"Strongest contributing signal: {top_signal[0].upper()} "
        f"(score: {top_signal[1][0]:.2f}, weight: {top_signal[1][1]:.0%}). "
        f"ML ensemble agreement: {ml_agreement}. "
        f"{'Coverage warning: fewer than 3 signals available, confidence capped at 65%. ' if coverage_warning else ''}"
    )
 
    return _build_verdict(
        verdict=verdict,
        confidence=round(confidence, 4),
        risk=risk,
        decisive_signal=None,
        conflict=False,
        coverage_warning=coverage_warning,
        ml_agreement=ml_agreement,
        signals=all_signals,
        summary=summary
    )
 
 
def _build_verdict(verdict, confidence, risk, decisive_signal, conflict, coverage_warning, ml_agreement, signals, summary):
    return {
        "verdict": verdict,
        "confidence": confidence,
        "risk_level": risk,
        "decisive_signal": decisive_signal,
        "conflict_detected": conflict,
        "coverage_warning": coverage_warning,
        "ml_ensemble_agreement": ml_agreement,
        "signals": signals,
        "summary": summary
    }
 