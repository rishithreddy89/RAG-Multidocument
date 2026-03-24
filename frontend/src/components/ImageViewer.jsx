/**
 * ImageViewer Component
 * Displays uploaded images from backend storage
 */

import React, { useState } from 'react';
import { ImageOff } from 'lucide-react';

const ImageViewer = ({ file }) => {
  const [loadError, setLoadError] = useState(false);

  const imageSource = file.documentId
    ? `http://localhost:8000/upload/documents/${file.documentId}/file`
    : file;

  if (loadError) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-50">
        <div className="text-center">
          <ImageOff className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 font-medium">Unable to load image</p>
          <p className="text-sm text-gray-400 mt-1">The image file could not be displayed</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-gray-50 overflow-auto p-6">
      <div className="w-full h-full flex items-center justify-center">
        <img
          src={imageSource}
          alt={file.name}
          className="max-w-full max-h-full object-contain rounded-lg shadow-lg bg-white"
          onError={() => setLoadError(true)}
        />
      </div>
    </div>
  );
};

export default ImageViewer;
