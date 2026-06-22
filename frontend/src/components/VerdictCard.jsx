function VerdictCard({ verdict }) {
  if (!verdict) return null

  const colors = {
    "AI GENERATED (CONFIRMED)": { border: "#DC2626", bg: "#FEF2F2", text: "#DC2626", badge: "#DC2626" },
    "AI GENERATED": { border: "#DC2626", bg: "#FEF2F2", text: "#DC2626", badge: "#DC2626" },
    "LIKELY AI GENERATED": { border: "#D97706", bg: "#FFFBEB", text: "#D97706", badge: "#D97706" },
    "AUTHENTIC (CONFIRMED)": { border: "#16A34A", bg: "#F0FDF4", text: "#16A34A", badge: "#16A34A" },
    "LIKELY AUTHENTIC": { border: "#16A34A", bg: "#F0FDF4", text: "#16A34A", badge: "#16A34A" },
    "INCONCLUSIVE — Conflicting signals, manual review recommended": { border: "#6B6563", bg: "#F5F4F0", text: "#6B6563", badge: "#6B6563" },
    "INCONCLUSIVE": { border: "#6B6563", bg: "#F5F4F0", text: "#6B6563", badge: "#6B6563" },
    "PRELIMINARY ANALYSIS ONLY": { border: "#6B6563", bg: "#F5F4F0", text: "#6B6563", badge: "#6B6563" },
  }

  const style = colors[verdict.verdict] || colors["INCONCLUSIVE"]
  const confidence = verdict.confidence ? `${(verdict.confidence * 100).toFixed(1)}%` : "N/A"

  return (
    <div style={{
      backgroundColor: style.bg,
      borderLeft: `4px solid ${style.border}`,
      borderRadius: "8px",
      padding: "24px",
      marginBottom: "16px"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <p style={{ fontSize: "11px", fontWeight: 600, letterSpacing: "0.08em", color: style.text, textTransform: "uppercase", marginBottom: "6px" }}>
            Verdict
          </p>
          <h2 style={{ fontSize: "22px", fontWeight: 700, color: "#1A1A1A", letterSpacing: "-0.3px" }}>
            {verdict.verdict}
          </h2>
        </div>
        <div style={{ textAlign: "right" }}>
          <p style={{ fontSize: "11px", fontWeight: 600, letterSpacing: "0.08em", color: "#6B6563", textTransform: "uppercase", marginBottom: "6px" }}>
            Confidence
          </p>
          <p style={{ fontSize: "28px", fontWeight: 700, color: style.text }}>
            {confidence}
          </p>
        </div>
      </div>

      <div style={{ display: "flex", gap: "8px", marginTop: "16px", flexWrap: "wrap" }}>
        <span style={{
          fontSize: "12px", fontWeight: 600, padding: "3px 10px",
          borderRadius: "4px", backgroundColor: style.border, color: "#fff"
        }}>
          {verdict.risk_level}
        </span>
        {verdict.decisive_signal && (
          <span style={{
            fontSize: "12px", fontWeight: 500, padding: "3px 10px",
            borderRadius: "4px", backgroundColor: "#1A1A1A", color: "#fff"
          }}>
            Decisive: {verdict.decisive_signal}
          </span>
        )}
        {verdict.conflict_detected && (
          <span style={{
            fontSize: "12px", fontWeight: 500, padding: "3px 10px",
            borderRadius: "4px", backgroundColor: "#D97706", color: "#fff"
          }}>
            ⚠ Conflict Detected
          </span>
        )}
        {verdict.coverage_warning && (
          <span style={{
            fontSize: "12px", fontWeight: 500, padding: "3px 10px",
            borderRadius: "4px", backgroundColor: "#6B6563", color: "#fff"
          }}>
            Low Signal Coverage
          </span>
        )}
      </div>

      {verdict.summary && (
        <p style={{ marginTop: "16px", fontSize: "13px", color: "#6B6563", lineHeight: "1.6" }}>
          {verdict.summary}
        </p>
      )}
    </div>
  )
}

export default VerdictCard