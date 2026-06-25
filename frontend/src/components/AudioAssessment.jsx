function AudioAssessment({ assessment }) {
  if (!assessment) return null

  const riskColors = {
    "HIGH": { border: "#DC2626", bg: "#FEF2F2", text: "#DC2626" },
    "MEDIUM": { border: "#D97706", bg: "#FFFBEB", text: "#D97706" },
    "LOW": { border: "#16A34A", bg: "#F0FDF4", text: "#16A34A" },
    "UNKNOWN": { border: "#6B6563", bg: "#F5F4F0", text: "#6B6563" }
  }

  const style = riskColors[assessment.risk_level] || riskColors["UNKNOWN"]
  const likelihood = assessment.synthesis_likelihood
  const likelihoodPct = likelihood !== null && likelihood !== undefined
    ? `${(likelihood * 100).toFixed(1)}%`
    : "N/A"

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
            Forensic Audio Assessment
          </p>
          <h2 style={{ fontSize: "18px", fontWeight: 700, color: "#1A1A1A", letterSpacing: "-0.3px" }}>
            {assessment.assessment}
          </h2>
        </div>
        <div style={{ textAlign: "right" }}>
          <p style={{ fontSize: "11px", fontWeight: 600, letterSpacing: "0.08em", color: "#6B6563", textTransform: "uppercase", marginBottom: "6px" }}>
            Synthesis Likelihood
          </p>
          <p style={{ fontSize: "28px", fontWeight: 700, color: style.text }}>
            {likelihoodPct}
          </p>
        </div>
      </div>

      <span style={{
        display: "inline-block",
        marginTop: "12px",
        fontSize: "12px",
        fontWeight: 600,
        padding: "3px 10px",
        borderRadius: "4px",
        backgroundColor: style.border,
        color: "#fff"
      }}>
        {assessment.risk_level}
      </span>

      {assessment.findings && assessment.findings.length > 0 && (
        <div style={{ marginTop: "16px" }}>
          {assessment.findings.map((finding, i) => (
            <div key={i} style={{
              display: "flex",
              gap: "8px",
              marginBottom: "6px",
              alignItems: "flex-start"
            }}>
              <span style={{ color: style.text, fontWeight: 700, flexShrink: 0 }}>·</span>
              <p style={{ fontSize: "13px", color: "#6B6563", lineHeight: "1.5" }}>{finding}</p>
            </div>
          ))}
        </div>
      )}

      {assessment.content_note && (
        <p style={{
          marginTop: "12px",
          fontSize: "12px",
          color: "#6B6563",
          fontStyle: "italic",
          padding: "8px 12px",
          backgroundColor: "rgba(0,0,0,0.04)",
          borderRadius: "4px"
        }}>
          {assessment.content_note}
        </p>
      )}
    </div>
  )
}

export default AudioAssessment