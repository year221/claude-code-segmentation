import React from 'react';
import type { SegmentationResult } from '../types';

interface ImageDisplayProps {
  result: SegmentationResult | null;
  isLoading: boolean;
}

const ImageDisplay: React.FC<ImageDisplayProps> = ({ result, isLoading }) => {
  if (isLoading) {
    return (
      <div className="image-display loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Processing image...</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="image-display empty">
        <p>Upload an image or enter a URL to see segmentation results</p>
      </div>
    );
  }

  return (
    <div className="image-display">
      <div className="image-comparison">
        <div className="image-container">
          <h3>Original Image</h3>
          <img
            src={`data:image/png;base64,${result.original_image}`}
            alt="Original"
            className="result-image"
          />
        </div>
        
        <div className="image-container">
          <h3>Segmentation Result</h3>
          <img
            src={`data:image/png;base64,${result.segmented_image}`}
            alt="Segmentation Result"
            className="result-image"
          />
        </div>
      </div>
      
      <div className="image-info">
        {result.filename && <p>File: {result.filename}</p>}
        {result.source_url && <p>Source: {result.source_url}</p>}
      </div>
    </div>
  );
};

export default ImageDisplay;