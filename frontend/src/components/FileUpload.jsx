/**
 * FileUpload Component
 * Drag-and-drop file upload with progress indicator
 */

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File } from 'lucide-react';

const FileUpload = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      acceptedFiles.forEach(file => {
        formData.append('files', file);
      });

      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      
      setTimeout(() => {
        onUploadSuccess && onUploadSuccess(acceptedFiles, data);
        setUploading(false);
        setUploadProgress(0);
      }, 500);

    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload files: ' + error.message);
      setUploading(false);
      setUploadProgress(0);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt']
    },
    multiple: true,
    disabled: uploading
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer
          transition-all duration-200 ease-in-out
          ${isDragActive 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 bg-gray-50 hover:border-primary-400 hover:bg-primary-50/50'
          }
          ${uploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          <div className="p-4 bg-white rounded-full shadow-sm">
            <Upload className={`w-12 h-12 ${isDragActive ? 'text-primary-500' : 'text-gray-400'}`} />
          </div>
          
          {uploading ? (
            <div className="w-full max-w-xs">
              <div className="text-sm font-medium text-gray-700 mb-2">
                Uploading... {uploadProgress}%
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div 
                  className="bg-primary-500 h-full transition-all duration-300 ease-out"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          ) : (
            <>
              <div>
                <p className="text-lg font-semibold text-gray-700">
                  {isDragActive ? 'Drop files here' : 'Drag & drop files here'}
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  or click to browse
                </p>
              </div>
              <div className="flex items-center space-x-2 text-xs text-gray-500">
                <File className="w-4 h-4" />
                <span>Supports PDF and TXT files</span>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
