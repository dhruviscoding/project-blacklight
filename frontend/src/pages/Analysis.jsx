import { useLocation, useNavigate } from 'react-router-dom'
import axios from 'axios'
import VerdictCard from '../components/VerdictCard'
import SignalBreakdown from '../components/SignalBreakdown'
import MetadataPanel from '../components/MetadataPanel'
import HashPanel from '../components/HashPanel'
import ForensicVisuals from '../components/ForensicVisuals'

function Analysis() {
  const location = useLocation()
  const navigate = useNavigate()
  const { result, file, mediaType } = location.state || {}

  async function downloadReport() {
    try {
      const response = await axios.post(
        'http://127.0.0.1:8000/report/generate',
        {
          analysis_result: result,
          filename: file,
          media_type: mediaType
        },
        { responseType: 'blob' }
      )
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `blacklight_report_${file}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      alert('Report generation failed. Make sure the backend is running.')
    }
  }

  if (!result) {
    return (
      <div style={{ minHeight: "100vh", backgroundColor: "#FAFAF8", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <p style={{ color: "#6B6563", marginBottom: "16px" }}>No analysis data found.</p>
          <button
            onClick={() => navigate("/")}
            style={{
              padding: "10px 20px",
              backgroundColor: "#D97757",
              color: "#FFFFFF",
              border: "none",
              borderRadius: "8px",
              fontFamily: "Inter, sans-serif",
              fontSize: "14px",
              fontWeight: 600,
              cursor: "pointer"
            }}
          >
            Start New Analysis
          </button>
        </div>
      </div>
    )
  }

  const signals = result.signals || {}

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#FAFAF8" }}>
      <div style={{ maxWidth: "800px", margin: "0 auto", padding: "48px 24px 80px" }}>

        <div style={{ marginBottom: "32px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <button
              onClick={() => navigate("/")}
              style={{
                background: "none",
                border: "none",
                color: "#6B6563",
                fontSize: "13px",
                cursor: "pointer",
                fontFamily: "Inter, sans-serif",
                padding: "0",
                display: "flex",
                alignItems: "center",
                gap: "4px"
              }}
            >
              ← New Analysis
            </button>
            <button
              onClick={downloadReport}
              style={{
                padding: "8px 16px",
                backgroundColor: "#D97757",
                color: "#FFFFFF",
                border: "none",
                borderRadius: "8px",
                fontFamily: "Inter, sans-serif",
                fontSize: "13px",
                fontWeight: 600,
                cursor: "pointer"
              }}
            >
              Download Report
            </button>
          </div>
          <h1 style={{ fontSize: "24px", fontWeight: 700, color: "#1A1A1A", letterSpacing: "-0.3px" }}>
            Analysis Report
          </h1>
          <p style={{ marginTop: "4px", fontSize: "14px", color: "#6B6563", fontFamily: "'JetBrains Mono', monospace" }}>
            {file} · {mediaType}
          </p>
        </div>

        <VerdictCard verdict={result.verdict} />

        <SignalBreakdown signals={signals} />

        <ForensicVisuals
          ela={signals.ela}
          fft={signals.fft}
          noise={signals.noise}
        />

        <MetadataPanel metadata={signals.metadata} />

        <HashPanel hashes={signals.hashes} />

        {result.reverse_search && result.reverse_search.links && (
          <div style={{
            backgroundColor: "#FFFFFF",
            borderRadius: "8px",
            border: "1px solid #E8E5E0",
            padding: "24px",
            marginBottom: "16px"
          }}>
            <h3 style={{ fontSize: "13px", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", color: "#6B6563", marginBottom: "16px" }}>
              Reverse Image Search
            </h3>
            <p style={{ fontSize: "13px", color: "#6B6563", marginBottom: "12px" }}>
              Open in external search engines to verify image origin and earliest appearance.
            </p>
            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
              {Object.entries(result.reverse_search.links).map(([engine, url]) => (
                <a
                  key={engine}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    padding: "8px 16px",
                    backgroundColor: "#F5F4F0",
                    border: "1px solid #E8E5E0",
                    borderRadius: "6px",
                    fontSize: "13px",
                    fontWeight: 500,
                    color: "#1A1A1A",
                    textDecoration: "none"
                  }}
                >
                  {engine.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}
                </a>
              ))}
            </div>
            <p style={{ fontSize: "11px", color: "#6B6563", marginTop: "12px" }}>
              Note: Links use a placeholder URL until cloud storage is configured. Full programmatic reverse search coming in Phase 2.
            </p>
          </div>
        )}

        {signals.c2pa && signals.c2pa.has_c2pa && signals.c2pa.raw_data && (
          <div style={{
            backgroundColor: "#FFFFFF",
            borderRadius: "8px",
            border: "1px solid #E8E5E0",
            padding: "24px",
            marginBottom: "16px"
          }}>
            <h3 style={{ fontSize: "13px", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase", color: "#6B6563", marginBottom: "16px" }}>
              C2PA Content Credentials
            </h3>
            <p style={{ fontSize: "13px", color: signals.c2pa.score === 0.95 ? "#DC2626" : "#16A34A", fontWeight: 600, marginBottom: "8px" }}>
              {signals.c2pa.finding}
            </p>
            <pre style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: "11px",
              color: "#6B6563",
              backgroundColor: "#F5F4F0",
              padding: "12px",
              borderRadius: "6px",
              overflow: "auto",
              maxHeight: "200px"
            }}>
              {JSON.stringify(signals.c2pa.raw_data, null, 2)}
            </pre>
          </div>
        )}

      </div>
    </div>
  )
}

export default Analysis