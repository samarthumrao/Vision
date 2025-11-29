import { useState, useEffect } from 'react'
import './index.css'

function App() {
  const [caption, setCaption] = useState("Waiting for scene...")
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    // Poll for captions
    const interval = setInterval(async () => {
      try {
        const res = await fetch('http://localhost:8000/status')
        const data = await res.json()
        setCaption(data.caption)
        setIsConnected(true)
      } catch (e) {
        console.error("Connection error", e)
        setIsConnected(false)
      }
    }, 1000) // Poll every second

    return () => clearInterval(interval)
  }, [])

  const handleReadText = async () => {
    try {
      setCaption("Reading text...")
      const res = await fetch('http://localhost:8000/read_text', { method: 'POST' })
      const data = await res.json()
      if (data.status === 'success') {
        setCaption(`OCR: ${data.text}`)
      } else {
        setCaption(`Error: ${data.message}`)
      }
    } catch (e) {
      console.error("OCR Error", e)
      setCaption("Failed to connect for OCR")
    }
  }

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'r' || e.key === 'R') {
        handleReadText()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return (
    <div className="container">
      <div className="header">
        <h1 className="title">Smart Vision AI</h1>
        <p className="subtitle">Real-time Object Detection & Scene Understanding</p>
      </div>

      <div className="status-badge">
        <div className="status-dot" style={{ background: isConnected ? '#00ff88' : '#ff4444', boxShadow: isConnected ? '0 0 10px #00ff88' : '0 0 10px #ff4444' }}></div>
        {isConnected ? "System Online" : "Connecting to Server..."}
      </div>

      <div className="video-container">
        {isConnected ? (
          <img
            src="http://localhost:8000/video_feed"
            alt="Live Video Feed"
            className="video-feed"
          />
        ) : (
          <div className="video-feed" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#111', color: '#666' }}>
            Waiting for video stream...
          </div>
        )}

        <div className="caption-overlay">
          <p className="caption-text">
            {caption || "Analyzing scene..."}
          </p>
        </div>
      </div>

      <div className="controls">
        <button onClick={handleReadText}>
          Read Text (Press 'R')
        </button>
      </div>
    </div>
  )
}

export default App
