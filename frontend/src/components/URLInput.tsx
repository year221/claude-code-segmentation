import React, { useState } from 'react';

interface URLInputProps {
  onSubmit: (url: string) => void;
  isLoading?: boolean;
}

const URLInput: React.FC<URLInputProps> = ({ onSubmit, isLoading }) => {
  const [url, setUrl] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onSubmit(url.trim());
    }
  };

  return (
    <div className="url-input">
      <h3>Or enter image URL</h3>
      <form onSubmit={handleSubmit} className="url-form">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/image.jpg"
          className="url-input-field"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!url.trim() || isLoading}
          className="url-submit-btn"
        >
          {isLoading ? 'Processing...' : 'Process Image'}
        </button>
      </form>
    </div>
  );
};

export default URLInput;