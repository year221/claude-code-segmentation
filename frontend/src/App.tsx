import { useState } from 'react'
import './App.css'
import ImageUploader from './components/ImageUploader'
import URLInput from './components/URLInput'
import ImageDisplay from './components/ImageDisplay'
import { uploadImage, segmentFromUrl } from './services/api'
import type { SegmentationResult, AxiosErrorResponse } from './types'

function App() {
  const [result, setResult] = useState<SegmentationResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileUpload = async (file: File) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const segmentationResult = await uploadImage(file)
      setResult(segmentationResult)
    } catch (err: unknown) {
      const errorMessage = err && typeof err === 'object' && 'response' in err 
        ? (err as AxiosErrorResponse).response?.data?.detail || 'Error processing image'
        : 'Error processing image';
      setError(errorMessage)
      console.error('Upload error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleUrlSubmit = async (url: string) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const segmentationResult = await segmentFromUrl(url)
      setResult(segmentationResult)
    } catch (err: unknown) {
      const errorMessage = err && typeof err === 'object' && 'response' in err 
        ? (err as AxiosErrorResponse).response?.data?.detail || 'Error processing image from URL'
        : 'Error processing image from URL';
      setError(errorMessage)
      console.error('URL processing error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Semantic Image Segmentation</h1>
        <p>Upload an image or provide a URL to see AI-powered segmentation results</p>
      </header>

      <main className="app-main">
        <div className="input-section">
          <ImageUploader onFileSelect={handleFileUpload} isLoading={isLoading} />
          <URLInput onSubmit={handleUrlSubmit} isLoading={isLoading} />
        </div>

        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
          </div>
        )}

        <div className="results-section">
          <ImageDisplay result={result} isLoading={isLoading} />
        </div>
      </main>
    </div>
  )
}

export default App
