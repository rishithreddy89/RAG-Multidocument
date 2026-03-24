/**
 * ImageViewer Component
 * Displays uploaded images from backend storage
 */

import React, { useMemo, useState } from 'react';
import { ImageOff } from 'lucide-react';

const ImageViewer = ({ file, activeBbox }) => {
  const [loadError, setLoadError] = useState(false);
  const [naturalSize, setNaturalSize] = useState({ width: 1, height: 1 });

  const imageSource = file.documentId
    ? `http://localhost:8000/upload/documents/${file.documentId}/file`
    : file;

  const bbox = useMemo(() => {
    if (!activeBbox) return null;
    if (Array.isArray(activeBbox) && activeBbox.length >= 4) {
      const parsed = activeBbox.map((v) => Number(v));
      if (parsed.every((v) => Number.isFinite(v))) return parsed;
    }
    return null;
  }, [activeBbox]);

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
        <div className="relative inline-block">
        <img
          src={imageSource}
          alt={file.name}
          className="max-w-full max-h-full object-contain rounded-lg shadow-lg bg-white"
          onError={() => setLoadError(true)}
          onLoad={(e) => {
            setNaturalSize({
              width: e.target.naturalWidth || 1,
              height: e.target.naturalHeight || 1,
            });
          }}
        />

        {bbox && (
          <div
            className="absolute border-2 border-amber-500 bg-amber-300/30 rounded-sm animate-pulse pointer-events-none"
            style={{
              left: `${(bbox[0] / naturalSize.width) * 100}%`,
              top: `${(bbox[1] / naturalSize.height) * 100}%`,
              width: `${(bbox[2] / naturalSize.width) * 100}%`,
              height: `${(bbox[3] / naturalSize.height) * 100}%`,
            }}
          />
        )}
        </div>
      </div>
    </div>
  );
};

export default ImageViewer;
