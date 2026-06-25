import FileUpload from '../components/FileUpload'
 
function Home() {
  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#FAFAF8" }}>
      <div style={{ maxWidth: "800px", margin: "0 auto", padding: "80px 24px 24px" }}>
 
        <div style={{ marginBottom: "56px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
            <div style={{
              width: "8px", height: "8px", borderRadius: "50%",
              backgroundColor: "#D97757"
            }} />
            <span style={{ fontSize: "12px", fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", color: "#6B6563" }}>
              Project Blacklight
            </span>
          </div>
          <h1 style={{
            fontSize: "36px", fontWeight: 700, color: "#1A1A1A",
            letterSpacing: "-0.5px", lineHeight: "1.2", marginBottom: "12px"
          }}>
            Digital Media<br />Forensics Platform
          </h1>
          <p style={{ fontSize: "16px", color: "#6B6563", lineHeight: "1.6", maxWidth: "480px" }}>
            Investigative-grade forensic analysis of images, audio, and video. Metadata extraction, C2PA verification, frequency domain analysis, and ML-based detection.
          </p>
        </div>
 
        <FileUpload />
 
        <div style={{ marginTop: "48px", display: "flex", gap: "24px", flexWrap: "wrap" }}>
          {[
            { label: "C2PA Verification", desc: "Cryptographic provenance" },
            { label: "ML Ensemble", desc: "CNN + ViT classifiers" },
            { label: "FFT Analysis", desc: "Frequency domain artifacts" },
            { label: "Noise Analysis", desc: "Sensor noise patterns" },
            { label: "Metadata Forensics", desc: "EXIF + IPTC + XMP" },
            { label: "ELA", desc: "Compression analysis" },
          ].map((signal, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <div style={{ width: "6px", height: "6px", borderRadius: "50%", backgroundColor: "#D97757", flexShrink: 0 }} />
              <div>
                <p style={{ fontSize: "13px", fontWeight: 600, color: "#1A1A1A" }}>{signal.label}</p>
                <p style={{ fontSize: "11px", color: "#6B6563" }}>{signal.desc}</p>
              </div>
            </div>
          ))}
        </div>
 
      </div>
    </div>
  )
}
 
export default Home