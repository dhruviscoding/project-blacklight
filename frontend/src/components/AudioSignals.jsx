function AudioSignals({ signals }) {
  if (!signals) return null

  const { metadata, spectral, edit_artifacts, speaker_consistency } = signals

  const Section = ({ title, children }) => (
    <div style={{
      backgroundColor: "#FFFFFF",
      borderRadius: "8px",
      border: "1px solid #E8E5E0",
      padding: "24px",
      marginBottom: "16px"
    }}>
      <h3 style={{ fontSize: "13px", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", color: "#6B6563", marginBottom: "16px" }}>
        {title}
      </h3>
      {children}
    </div>
  )

  const Row = ({ label, value, mono = false, highlight = null }) => (
    <tr style={{ borderBottom: "1px solid #F5F4F0" }}>
      <td style={{ padding: "6px 0", color: "#6B6563", fontSize: "13px", width: "200px" }}>{label}</td>
      <td style={{
        padding: "6px 0",
        fontSize: "13px",
        fontFamily: mono ? "'JetBrains Mono', monospace" : "Inter, sans-serif",
        color: highlight || "#1A1A1A"
      }}>
        {value ?? "N/A"}
      </td>
    </tr>
  )

  return (
    <div>

      {/* Speaker Consistency */}
      {speaker_consistency && (
        <Section title="Speaker Consistency">
          <div style={{
            padding: "12px",
            borderRadius: "6px",
            backgroundColor: speaker_consistency.consistent === false ? "#FEF2F2" : speaker_consistency.consistent === true ? "#F0FDF4" : "#F5F4F0",
            marginBottom: "12px"
          }}>
            <p style={{
              fontSize: "14px",
              fontWeight: 600,
              color: speaker_consistency.consistent === false ? "#DC2626" : speaker_consistency.consistent === true ? "#16A34A" : "#6B6563"
            }}>
              {speaker_consistency.finding}
            </p>
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <tbody>
              <Row label="Segments analyzed" value={speaker_consistency.segments_analyzed} />
              {speaker_consistency.mean_similarity !== undefined && (
                <Row label="Mean similarity" value={`${(speaker_consistency.mean_similarity * 100).toFixed(1)}%`} />
              )}
              {speaker_consistency.min_similarity !== undefined && (
                <Row label="Min similarity" value={`${(speaker_consistency.min_similarity * 100).toFixed(1)}%`} />
              )}
              {speaker_consistency.identity_shift_timestamps && speaker_consistency.identity_shift_timestamps.length > 0 && (
                <Row
                  label="Identity shifts at"
                  value={`${speaker_consistency.identity_shift_timestamps.join(", ")}s`}
                  highlight="#DC2626"
                />
              )}
            </tbody>
          </table>
        </Section>
      )}

      {/* Edit Artifacts */}
      {edit_artifacts && (
        <Section title="Edit Artifact Detection">
          <div style={{
            padding: "12px",
            borderRadius: "6px",
            backgroundColor: edit_artifacts.edit_artifacts_detected ? "#FEF2F2" : "#F0FDF4",
            marginBottom: "12px"
          }}>
            <p style={{
              fontSize: "14px",
              fontWeight: 600,
              color: edit_artifacts.edit_artifacts_detected ? "#DC2626" : "#16A34A"
            }}>
              {edit_artifacts.edit_artifacts_detected ? "Edit artifacts detected" : "No significant edit artifacts detected"}
            </p>
          </div>
          {edit_artifacts.findings && edit_artifacts.findings.map((f, i) => (
            <p key={i} style={{ fontSize: "13px", color: "#6B6563", marginBottom: "4px" }}>· {f}</p>
          ))}
          {edit_artifacts.splice_points && edit_artifacts.splice_points.length > 0 && (
            <div style={{ marginTop: "8px" }}>
              <p style={{ fontSize: "12px", fontWeight: 600, color: "#6B6563", marginBottom: "4px" }}>SPLICE POINTS (seconds)</p>
              <p style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: "12px", color: "#DC2626" }}>
                {edit_artifacts.splice_points.join(", ")}
              </p>
            </div>
          )}
        </Section>
      )}

      {/* Spectral Analysis */}
      {spectral && !spectral.error && (
        <Section title="Spectral Analysis">
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <tbody>
              <Row label="Duration" value={spectral.duration_seconds ? `${spectral.duration_seconds}s` : null} />
              <Row label="Sample rate" value={spectral.sample_rate ? `${spectral.sample_rate} Hz` : null} />
              {spectral.pitch && (
                <>
                  <Row label="Pitch mean" value={spectral.pitch.mean_hz ? `${spectral.pitch.mean_hz} Hz` : null} />
                  <Row label="Pitch std" value={spectral.pitch.std_hz ? `${spectral.pitch.std_hz} Hz` : null} />
                  <Row label="Pitch flatness index" value={spectral.pitch.flatness_index}
                    highlight={spectral.pitch.flatness_index !== null && spectral.pitch.flatness_index < 0.15 ? "#D97706" : null}
                  />
                  <Row label="Voiced ratio" value={spectral.pitch.voiced_ratio} />
                </>
              )}
              {spectral.silence && (
                <>
                  <Row label="Silence ratio" value={spectral.silence.silence_ratio} />
                  <Row label="Pause count" value={spectral.silence.num_pauses} />
                </>
              )}
              <Row label="HNR (dB)" value={spectral.harmonic_to_noise_ratio_db} />
              <Row label="Spectral flatness" value={spectral.spectral_flatness} mono />
            </tbody>
          </table>
          {spectral.synthesis_indicators && spectral.synthesis_indicators.length > 0 && (
            <div style={{ marginTop: "12px" }}>
              <p style={{ fontSize: "12px", fontWeight: 600, color: "#D97706", marginBottom: "6px" }}>SYNTHESIS INDICATORS</p>
              {spectral.synthesis_indicators.map((s, i) => (
                <p key={i} style={{ fontSize: "12px", color: "#6B6563", marginBottom: "4px" }}>· {s}</p>
              ))}
            </div>
          )}
        </Section>
      )}

      {/* Audio Metadata */}
      {metadata && !metadata.error && (
        <Section title="Audio Metadata">
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <tbody>
              <Row label="Format" value={metadata.format} />
              <Row label="Duration" value={metadata.duration ? `${metadata.duration}s` : null} />
              <Row label="Bitrate" value={metadata.bitrate ? `${(metadata.bitrate / 1000).toFixed(0)} kbps` : null} />
              <Row label="Sample rate" value={metadata.sample_rate ? `${metadata.sample_rate} Hz` : null} />
              <Row label="Channels" value={metadata.channels} />
            </tbody>
          </table>
        </Section>
      )}

    </div>
  )
}

export default AudioSignals