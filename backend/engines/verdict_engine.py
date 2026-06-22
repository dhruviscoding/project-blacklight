def run_verdict_engine(signals: dict) -> dict:
    """
    Weighted evidence fusion engine for AI-generated image detection.

    Signal weights (research-backed):
    - CNN + ViT ML ensemble: 0.40 (averaged into one combined ML score)
    - FFT Analysis: 0.25
    - Noise Analysis: 0.20
    - Metadata Analysis: 0.10
    - ELA: 0.05

    Special logic:
    - C2PA: priority override — bypasses weighted average if decisive
    - Conflict detection: flags disagreement between signal categories
    - Coverage penalty: caps confidence if fewer than 3 signals available
    - Cross-signal coherence: checks if all 3 categories agree
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

    all_signals = {
        "C2PA Verification": c2pa,
        "CNN Classifier": cnn,
        "Modern AI Classifier": vit,
        "FFT Frequency Analysis": fft,
        "Noise Analysis": noise,
        "Metadata Analysis": metadata,
        "Error Level Analysis": ela
    }

    # ----------------------------------------------------------------
    # Step 2 — C2PA priority override
    # ----------------------------------------------------------------
    if c2pa is not None:
        if c2pa["score"] == 0.95:
            return _build_verdict(
                verdict="AI GENERATED (CONFIRMED)",
                confidence=0.95,
                risk="CRITICAL",
                decisive_signal="C2PA Verification",
                conflict=False,
                coverage_warning=False,
                signals=all_signals,
                summary=f"C2PA Content Credentials cryptographically confirm AI generation. "
                        f"Source: {c2pa.get('raw_data', {}).get('manifests', {}).get('', {}).get('claim_generator', 'Unknown AI tool')}. "
                        f"This overrides probabilistic signals."
            )
        if c2pa["score"] == 0.05:
            return _build_verdict(
                verdict="AUTHENTIC (CONFIRMED)",
                confidence=0.95,
                risk="LOW",
                decisive_signal="C2PA Verification",
                conflict=False,
                coverage_warning=False,
                signals=all_signals,
                summary="C2PA Content Credentials cryptographically confirm authentic origin. "
                        "This overrides probabilistic signals."
            )

    # ----------------------------------------------------------------
    # Step 3 — Combine ML signals into one ensemble score
    # ----------------------------------------------------------------
    ml_scores = [s for s in [
        cnn["score"] if cnn and cnn["score"] is not None else None,
        vit["score"] if vit and vit["score"] is not None else None
    ] if s is not None]

    combined_ml = sum(ml_scores) / len(ml_scores) if ml_scores else None

    # Check if the two ML classifiers strongly disagree
    ml_internal_conflict = False
    if cnn and vit and cnn["score"] is not None and vit["score"] is not None:
        if abs(cnn["score"] - vit["score"]) > 0.4:
            ml_internal_conflict = True

    # ----------------------------------------------------------------
    # Step 4 — Build weighted signal pool with dynamic reweighting
    # ----------------------------------------------------------------
    base_weights = {
        "ml": (combined_ml, 0.40),
        "fft": (fft["score"] if fft and fft["score"] is not None else None, 0.25),
        "noise": (noise["score"] if noise and noise["score"] is not None else None, 0.20),
        "metadata": (metadata["score"] if metadata and metadata["score"] is not None else None, 0.10),
        "ela": (ela["score"] if ela and ela["score"] is not None else None, 0.05),
    }

    # Filter out None scores, redistribute weights proportionally
    available = {k: v for k, v in base_weights.items() if v[0] is not None}
    total_weight = sum(w for _, w in available.values())
    normalized = {k: (score, weight / total_weight) for k, (score, weight) in available.items()}

    # Coverage check — how many of the 5 signal categories are available
    coverage = len(available)
    coverage_warning = coverage < 3

    # ----------------------------------------------------------------
    # Step 5 — Compute category scores for conflict detection
    # ----------------------------------------------------------------
    ml_category_score = combined_ml
    statistical_scores = [s for s in [
        fft["score"] if fft and fft["score"] is not None else None,
        noise["score"] if noise and noise["score"] is not None else None,
        ela["score"] if ela and ela["score"] is not None else None
    ] if s is not None]
    statistical_category_score = sum(statistical_scores) / len(statistical_scores) if statistical_scores else None
    provenance_category_score = metadata["score"] if metadata and metadata["score"] is not None else None

    # Cross-signal coherence — do all 3 categories agree?
    category_scores = [s for s in [ml_category_score, statistical_category_score, provenance_category_score] if s is not None]
    conflict_detected = False
    coherence_bonus = 0.0

    if len(category_scores) >= 2:
        max_cat = max(category_scores)
        min_cat = min(category_scores)
        if max_cat - min_cat > 0.4:
            conflict_detected = True
        elif max_cat - min_cat < 0.15:
            coherence_bonus = 0.05  # all categories agree, slight confidence boost

    # Also flag if ML classifiers internally disagree
    if ml_internal_conflict:
        conflict_detected = True

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
            signals=all_signals,
            summary=f"Signals from different analysis categories disagree strongly. "
                    f"{'ML classifiers internally disagree. ' if ml_internal_conflict else ''}"
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

    # Build summary
    top_signal = max(normalized.items(), key=lambda x: x[1][0] * x[1][1])
    summary = (
        f"{coverage} of 5 signal categories available. "
        f"Weighted confidence: {confidence:.0%}. "
        f"Strongest contributing signal: {top_signal[0].upper()} "
        f"(score: {top_signal[1][0]:.2f}, weight: {top_signal[1][1]:.0%}). "
        f"{'Coverage warning: fewer than 3 signals available, confidence capped at 65%. ' if coverage_warning else ''}"
    )

    return _build_verdict(
        verdict=verdict,
        confidence=round(confidence, 4),
        risk=risk,
        decisive_signal=None,
        conflict=False,
        coverage_warning=coverage_warning,
        signals=all_signals,
        summary=summary
    )


def _build_verdict(verdict, confidence, risk, decisive_signal, conflict, coverage_warning, signals, summary):
    return {
        "verdict": verdict,
        "confidence": confidence,
        "risk_level": risk,
        "decisive_signal": decisive_signal,
        "conflict_detected": conflict,
        "coverage_warning": coverage_warning,
        "signals": signals,
        "summary": summary
    }