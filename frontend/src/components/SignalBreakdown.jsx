function SignalBreakdown({ signals }) {
  if (!signals) return null

  const signalList = Object.entries(signals)
    .filter(([_, signal]) => signal && signal.name)
    .map(([key, signal]) => signal)

  if (signalList.length === 0) return null

  return (
    <div style={{
      backgroundColor: "#FFFFFF",
      borderRadius: "8px",
      border: "1px solid #E8E5E0",
      padding: "24px",
      marginBottom: "16px"
    }}>
      <h3 style={{ fontSize: "13px", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", color: "#6B6563", marginBottom: "16px" }}>
        Signal Breakdown
      </h3>

      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        {signalList.map((signal, i) => {
          const score = signal.score
          const hasScore = score !== null && score !== undefined
          const scorePercent = hasScore ? Math.round(score * 100) : null

          const barColor = !hasScore ? "#E8E5E0"
            : score > 0.8 ? "#DC2626"
            : score > 0.6 ? "#D97706"
            : score > 0.35 ? "#6B6563"
            : "#16A34A"

          return (
            <div key={i}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                <div>
                  <span style={{ fontSize: "14px", fontWeight: 600, color: "#1A1A1A" }}>
                    {signal.name}
                  </span>
                  <span style={{ fontSize: "12px", color: "#6B6563", marginLeft: "8px" }}>
                    {signal.category}
                  </span>
                </div>
                <span style={{ fontSize: "14px", fontWeight: 600, color: barColor, fontFamily: "'JetBrains Mono', monospace" }}>
                  {hasScore ? `${scorePercent}%` : "N/A"}
                </span>
              </div>

              <div style={{ height: "4px", backgroundColor: "#F5F4F0", borderRadius: "2px", overflow: "hidden" }}>
                <div style={{
                  height: "100%",
                  width: hasScore ? `${scorePercent}%` : "0%",
                  backgroundColor: barColor,
                  borderRadius: "2px",
                  transition: "width 0.6s ease"
                }} />
              </div>

              {signal.finding && (
                <p style={{ fontSize: "12px", color: "#6B6563", marginTop: "6px", lineHeight: "1.5" }}>
                  {signal.finding}
                </p>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default SignalBreakdown