/**
 * TextViewer Component
 * Clean, readable text file viewer
 */

import React, { useState, useEffect } from 'react';
import { FileText } from 'lucide-react';

const TextViewer = ({ file }) => {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      setContent(e.target.result);
      setLoading(false);
    };
    
    reader.onerror = () => {
      setContent('Error loading file');
      setLoading(false);
    };
    
    reader.readAsText(file);
  }, [file]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="h-full bg-white overflow-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 shadow-sm z-10">
        <div className="flex items-center space-x-3">
          <FileText className="w-5 h-5 text-blue-500" />
          <div>
            <h3 className="font-semibold text-gray-800">{file.name}</h3>
            <p className="text-xs text-gray-500">{content.split('\n').length} lines</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-8">
        <pre className="whitespace-pre-wrap font-mono text-sm text-gray-700 leading-relaxed">
          {content}
        </pre>
      </div>
    </div>
  );
};

export default TextViewer;
