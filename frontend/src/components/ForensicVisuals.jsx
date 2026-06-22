function ForensicVisuals({ ela, fft, noise }) {
  const visuals = [
    { label: "Error Level Analysis", data: ela, description: "Uniform error levels suggest single-pass export" },
    { label: "FFT Frequency Analysis", data: fft, description: "Periodic high-frequency artifacts indicate GAN upsampling" },
    { label: "Noise Analysis", data: noise, description: "Unnaturally smooth noise is inconsistent with camera sensors" },
  ].filter(v => v.data && v.data.visualization)

  if (visuals.length === 0) return null

  return (
    <div style={{
      backgroundColor: "#FFFFFF",
      borderRadius: "8px",
      border: "1px solid #E8E5E0",
      padding: "24px",
      marginBottom: "16px"
    }}>
      <h3 style={{ fontSize: "13px", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", color: "#6B6563", marginBottom: "16px" }}>
        Forensic Visualizations
      </h3>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px" }}>
        {visuals.map((visual, i) => (
          <div key={i}>
            <img
              src={visual.data.visualization}
              alt={visual.label}
              style={{
                width: "100%",
                borderRadius: "6px",
                border: "1px solid #E8E5E0",
                display: "block"
              }}
            />
            <p style={{ fontSize: "12px", fontWeight: 600, color: "#1A1A1A", marginTop: "8px" }}>
              {visual.label}
            </p>
            <p style={{ fontSize: "11px", color: "#6B6563", marginTop: "2px", lineHeight: "1.4" }}>
              {visual.description}
            </p>
            {visual.data.raw_data && (
              <p style={{ fontSize: "11px", color: "#6B6563", marginTop: "4px", fontFamily: "'JetBrains Mono', monospace" }}>
                Score: {(visual.data.score * 100).toFixed(0)}%
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default ForensicVisuals