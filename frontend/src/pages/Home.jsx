import FileUpload from '../components/FileUpload'

function Home() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#FAFAF8' }}>
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '80px 24px 24px' }}>
        <div style={{ marginBottom: '48px' }}>
          <h1 style={{
            fontSize: '32px',
            fontWeight: 700,
            color: '#1A1A1A',
            letterSpacing: '-0.5px'
          }}>
            Project Blacklight
          </h1>
          <p style={{
            marginTop: '8px',
            fontSize: '16px',
            color: '#6B6563'
          }}>
            AI-generated media forensics. Upload an image, audio, or video file to begin analysis.
          </p>
        </div>
        <FileUpload />
      </div>
    </div>
  )
}

export default Home