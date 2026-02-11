/**
 * ViewerPanel Component
 * Document viewer with maximize/restore controls
 */

import React from 'react';
import { Maximize2, Minimize2, FileQuestion } from 'lucide-react';
import DocumentViewer from './DocumentViewer';

const ViewerPanel = ({ 
  file, 
  isMaximized, 
  onToggleMaximize,
  style 
}) => {
  return (
    <div 
      className="flex flex-col bg-gray-50 overflow-hidden transition-all duration-300"
      style={style}
    >
      {/* Viewer Header */}
      <div className="flex-shrink-0 flex items-center justify-between px-6 py-3 bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center space-x-3">
          {file ? (
            <>
              <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-indigo-500 rounded-lg flex items-center justify-center">
                <FileQuestion className="w-5 h-5 text-white" />
              </div>
              <div className="max-w-md">
                <h3 className="font-semibold text-gray-800 truncate">{file.name}</h3>
                <p className="text-xs text-gray-500">
                  {(file.size / 1024).toFixed(1)} KB
                </p>
              </div>
            </>
          ) : (
            <h3 className="font-semibold text-gray-800">Document Viewer</h3>
          )}
        </div>

        <button
          onClick={onToggleMaximize}
          className="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-all duration-200"
          title={isMaximized ? 'Restore' : 'Maximize'}
        >
          {isMaximized ? (
            <Minimize2 className="w-5 h-5" />
          ) : (
            <Maximize2 className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* Document Content */}
      <div className="flex-1 overflow-hidden">
        <DocumentViewer file={file} />
      </div>
    </div>
  );
};

export default ViewerPanel;
