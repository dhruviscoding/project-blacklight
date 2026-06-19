import { useState, useRef } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

function FileUpload() {
  const [dragging, setDragging] = useState(false)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)
  const navigate = useNavigate()

  const ACCEPTED_TYPES = [
    'image/jpeg', 'image/png', 'image/webp', 'image/tiff',
    'audio/mpeg', 'audio/wav', 'audio/flac',
    'video/mp4', 'video/quicktime', 'video/x-msvideo'
  ]

  const MAX_SIZE = 50 * 1024 * 1024 // 50MB

  function getMediaType(file) {
    if (file.type.startsWith('image')) return 'image'
    if (file.type.startsWith('audio')) return 'audio'
    if (file.type.startsWith('video')) return 'video'
    return null
  }

  function handleFile(f) {
    setError(null)
    if (!ACCEPTED_TYPES.includes(f.type)) {
      setError('Unsupported file type. Please upload an image, audio, or video file.')
      return
    }
    if (f.size > MAX_SIZE) {
      setError('File too large. Maximum size is 50MB.')
      return
    }
    setFile(f)
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  async function handleAnalyze() {
    if (!file) return
    setLoading(true)
    setError(null)
    const mediaType = getMediaType(file)
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await axios.post(`http://127.0.0.1:8000/analyze/${mediaType}`, formData)
      navigate('/analysis', { state: { result: res.data, file: file.name, mediaType } })
    } catch (err) {
      setError('Analysis failed. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '24px' }}>
      <div
        onClick={() => fileInputRef.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${dragging ? '#D97757' : '#E8E5E0'}`,
          borderRadius: '12px',
          padding: '48px 24px',
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: dragging ? '#FFF8F5' : '#FFFFFF',
          transition: 'all 0.2s ease'
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*,audio/*,video/*"
          style={{ display: 'none' }}
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {file ? (
          <div>
            <p style={{ fontWeight: 600, color: '#1A1A1A' }}>{file.name}</p>
            <p style={{ color: '#6B6563', fontSize: '14px', marginTop: '4px' }}>
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        ) : (
          <div>
            <p style={{ fontWeight: 500, color: '#1A1A1A' }}>Drop a file here or click to upload</p>
            <p style={{ color: '#6B6563', fontSize: '14px', marginTop: '8px' }}>
              Images, audio, or video — max 50MB
            </p>
          </div>
        )}
      </div>

      {error && (
        <p style={{ color: '#DC2626', fontSize: '14px', marginTop: '12px' }}>{error}</p>
      )}

      {file && !loading && (
        <button
          onClick={handleAnalyze}
          style={{
            marginTop: '16px',
            width: '100%',
            padding: '12px',
            backgroundColor: '#D97757',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '8px',
            fontFamily: 'Inter, sans-serif',
            fontSize: '15px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          Analyze
        </button>
      )}

      {loading && (
        <div style={{ marginTop: '16px', textAlign: 'center' }}>
          <p style={{ color: '#6B6563' }}>Analyzing...</p>
          <div style={{
            marginTop: '8px',
            height: '3px',
            backgroundColor: '#E8E5E0',
            borderRadius: '2px',
            overflow: 'hidden'
          }}>
            <div style={{
              height: '100%',
              width: '40%',
              backgroundColor: '#D97757',
              borderRadius: '2px',
              animation: 'slide 1.5s infinite ease-in-out'
            }} />
          </div>
        </div>
      )}
    </div>
  )
}

export default FileUpload