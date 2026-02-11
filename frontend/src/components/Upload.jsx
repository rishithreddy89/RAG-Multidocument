/**
 * Upload component for uploading multiple documents.
 * Phase 1: Save files to backend
 * Phase 2: Will automatically process and index in ChromaDB
 */

import React, { useState } from 'react';
import { uploadDocuments } from '../services/api';
import './Upload.css';

const Upload = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });

  /**
   * Handle file selection.
   */
  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);
    setStatus({ type: '', message: '' });
  };

  /**
   * Handle file upload.
   */
  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setStatus({ type: 'error', message: 'Please select at least one file' });
      return;
    }

    setUploading(true);
    setStatus({ type: '', message: '' });

    try {
      // Create FileList-like object
      const fileList = selectedFiles.reduce((dataTransfer, file) => {
        dataTransfer.items.add(file);
        return dataTransfer;
      }, new DataTransfer()).files;

      const response = await uploadDocuments(fileList);
      
      setStatus({
        type: 'success',
        message: `${response.message}\nFiles: ${response.files.join(', ')}`
      });
      
      // Clear selection after successful upload
      setSelectedFiles([]);
      // Reset file input
      document.getElementById('file-input').value = '';
    } catch (error) {
      setStatus({
        type: 'error',
        message: error.message
      });
    } finally {
      setUploading(false);
    }
  };

  /**
   * Remove a file from selection.
   */
  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="upload-container">
      <div className="upload-header">
        <h2>📁 Upload Documents</h2>
        <p className="upload-subtitle">
          Supported formats: PDF, TXT
        </p>
      </div>

      <div className="upload-content">
        <div className="file-input-wrapper">
          <input
            id="file-input"
            type="file"
            multiple
            accept=".pdf,.txt"
            onChange={handleFileChange}
            disabled={uploading}
            className="file-input"
          />
          <label htmlFor="file-input" className="file-input-label">
            📎 Choose Files
          </label>
        </div>

        {selectedFiles.length > 0 && (
          <div className="selected-files">
            <h3>Selected Files ({selectedFiles.length})</h3>
            <ul className="file-list">
              {selectedFiles.map((file, index) => (
                <li key={index} className="file-item">
                  <span className="file-name">
                    {file.name}
                    <span className="file-size">
                      ({(file.size / 1024).toFixed(1)} KB)
                    </span>
                  </span>
                  <button
                    className="remove-button"
                    onClick={() => removeFile(index)}
                    disabled={uploading}
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <button
          className="upload-button"
          onClick={handleUpload}
          disabled={uploading || selectedFiles.length === 0}
        >
          {uploading ? '⏳ Uploading...' : '☁️ Upload Documents'}
        </button>

        {status.message && (
          <div className={`status-message ${status.type}`}>
            {status.message}
          </div>
        )}

        <div className="upload-info">
          <h3>ℹ️ Phase 1 Info</h3>
          <ul>
            <li>Documents are saved to <code>backend/data/documents/</code></li>
            <li>No processing happens yet (RAG coming in Phase 2)</li>
            <li>Phase 2 will add: document parsing, chunking, embeddings, ChromaDB indexing</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Upload;
