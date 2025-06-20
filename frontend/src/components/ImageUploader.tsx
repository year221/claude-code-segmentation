import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface ImageUploaderProps {
  onFileSelect: (file: File) => void;
  isLoading?: boolean;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({ onFileSelect, isLoading }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    multiple: false,
    disabled: isLoading
  });

  return (
    <div className="image-uploader">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${isLoading ? 'disabled' : ''}`}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the image here...</p>
        ) : (
          <div className="dropzone-content">
            <p>Drag & drop an image here, or click to select</p>
            <p className="dropzone-hint">Supports JPEG, PNG, WebP</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageUploader;