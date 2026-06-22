import { useState } from 'react'

function HashPanel({ hashes }) {
  if (!hashes) return null

  const [copied, setCopied] = useState(null)

  const { cryptographic, perceptual } = hashes

  function copyToClipboard(key, value) {
    navigator.clipboard.writeText(value)
    setCopied(key)
    setTimeout(() => setCopied(null), 2000)
  }

  const HashRow = ({ label, value }) => (
    <tr style={{ borderBottom: "1px solid #F5F4F0" }}>
      <td style={{ padding: "8px 0", color: "#6B6563", fontSize: "12px", width: "100px", fontWeight: 600 }}>
        {label}
      </td>
      <td style={{ padding: "8px 0", fontFamily: "'JetBrains Mono', monospace", fontSize: "12px", color: "#1A1A1A", wordBreak: "break-all" }}>
        {value}
      </td>
      <td style={{ padding: "8px 0", textAlign: "right", width: "60px" }}>
        <button
          onClick={() => copyToClipboard(label, value)}
          style={{
            fontSize: "11px",
            padding: "2px 8px",
            borderRadius: "4px",
            border: "1px solid #E8E5E0",
            backgroundColor: copied === label ? "#16A34A" : "#FFFFFF",
            color: copied === label ? "#FFFFFF" : "#6B6563",
            cursor: "pointer",
            fontFamily: "Inter, sans-serif",
            transition: "all 0.2s"
          }}
        >
          {copied === label ? "Copied" : "Copy"}
        </button>
      </td>
    </tr>
  )

  return (
    <div style={{
      backgroundColor: "#FFFFFF",
      borderRadius: "8px",
      border: "1px solid #E8E5E0",
      padding: "24px",
      marginBottom: "16px"
    }}>
      <h3 style={{ fontSize: "13px", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", color: "#6B6563", marginBottom: "16px" }}>
        File Hashes
      </h3>

      {cryptographic && (
        <div style={{ marginBottom: "20px" }}>
          <p style={{ fontSize: "12px", fontWeight: 600, color: "#6B6563", marginBottom: "8px" }}>CRYPTOGRAPHIC</p>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <tbody>
              <HashRow label="MD5" value={cryptographic.md5} />
              <HashRow label="SHA-1" value={cryptographic.sha1} />
              <HashRow label="SHA-256" value={cryptographic.sha256} />
              <HashRow label="SHA-512" value={cryptographic.sha512} />
            </tbody>
          </table>
        </div>
      )}

      {perceptual && (
        <div>
          <p style={{ fontSize: "12px", fontWeight: 600, color: "#6B6563", marginBottom: "8px" }}>PERCEPTUAL</p>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <tbody>
              <HashRow label="pHash" value={perceptual.phash} />
              <HashRow label="dHash" value={perceptual.dhash} />
              <HashRow label="aHash" value={perceptual.ahash} />
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default HashPanel