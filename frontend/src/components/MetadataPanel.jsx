function MetadataPanel({ metadata }) {
  if (!metadata || !metadata.raw_data) return null

  const { exif, iptc, xmp, gps, timestamps, tampering } = metadata.raw_data

  const hasExif = exif && Object.keys(exif).length > 0
  const hasIptc = iptc && Object.keys(iptc).length > 0
  const hasXmp = xmp && Object.keys(xmp).length > 0

  return (
    <div style={{
      backgroundColor: "#FFFFFF",
      borderRadius: "8px",
      border: "1px solid #E8E5E0",
      padding: "24px",
      marginBottom: "16px"
    }}>
      <h3 style={{ fontSize: "13px", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", color: "#6B6563", marginBottom: "16px" }}>
        Metadata
      </h3>

      {gps && gps.has_gps && (
        <div style={{ marginBottom: "16px", padding: "12px", backgroundColor: "#F5F4F0", borderRadius: "6px" }}>
          <p style={{ fontSize: "12px", fontWeight: 600, color: "#6B6563", marginBottom: "4px" }}>GPS COORDINATES</p>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "13px", color: "#1A1A1A" }}>
            {gps.latitude}, {gps.longitude}
            {gps.altitude && ` · ${gps.altitude}m`}
          </p>
        </div>
      )}

      {timestamps && (
        <div style={{ marginBottom: "16px" }}>
          <p style={{ fontSize: "12px", fontWeight: 600, color: "#6B6563", marginBottom: "8px" }}>TIMESTAMPS</p>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
            <tbody>
              {[
                ["Date Original", timestamps.date_original],
                ["Date Digitized", timestamps.date_digitized],
                ["File Modified", timestamps.file_modify_date],
                ["File Created", timestamps.file_create_date],
              ].map(([label, value]) => value && (
                <tr key={label} style={{ borderBottom: "1px solid #F5F4F0" }}>
                  <td style={{ padding: "6px 0", color: "#6B6563", width: "140px" }}>{label}</td>
                  <td style={{ padding: "6px 0", fontFamily: "'JetBrains Mono', monospace", color: "#1A1A1A" }}>{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {timestamps.inconsistent && (
            <p style={{ fontSize: "12px", color: "#D97706", marginTop: "8px" }}>
              ⚠ Timestamp inconsistency detected
            </p>
          )}
        </div>
      )}

      {tampering && tampering.software_detected && (
        <div style={{ marginBottom: "16px", padding: "12px", backgroundColor: tampering.ai_tool_match ? "#FEF2F2" : "#F5F4F0", borderRadius: "6px" }}>
          <p style={{ fontSize: "12px", fontWeight: 600, color: "#6B6563", marginBottom: "4px" }}>SOFTWARE DETECTED</p>
          <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "13px", color: tampering.ai_tool_match ? "#DC2626" : "#1A1A1A" }}>
            {tampering.software_detected}
            {tampering.ai_tool_match && " — AI generation tool"}
          </p>
        </div>
      )}

      {hasExif && (
        <div style={{ marginBottom: "16px" }}>
          <p style={{ fontSize: "12px", fontWeight: 600, color: "#6B6563", marginBottom: "8px" }}>EXIF</p>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
            <tbody>
              {Object.entries(exif).map(([key, value]) => (
                <tr key={key} style={{ borderBottom: "1px solid #F5F4F0" }}>
                  <td style={{ padding: "5px 0", color: "#6B6563", width: "200px" }}>{key}</td>
                  <td style={{ padding: "5px 0", fontFamily: "'JetBrains Mono', monospace", color: "#1A1A1A", wordBreak: "break-all" }}>{String(value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!hasExif && !hasIptc && !hasXmp && (
        <p style={{ fontSize: "13px", color: "#6B6563" }}>No EXIF, IPTC, or XMP metadata found in this file.</p>
      )}
    </div>
  )
}

export default MetadataPanel