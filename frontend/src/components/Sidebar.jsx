/**
 * Sidebar Component
 * Document list panel with file upload
 */

import React from 'react';
import { FolderOpen } from 'lucide-react';
import FileUpload from './FileUpload';
import FileList from './FileList';

const Sidebar = ({ 
  width, 
  isHidden,
  uploadedFiles, 
  selectedFile, 
  onSelectFile, 
  onDeleteFile,
  onUploadSuccess,
  showUpload,
  setShowUpload,
  selectedDocumentIds,
  onToggleDocument
}) => {
  if (isHidden) return null;

  return (
    <div 
      className="flex flex-col bg-white border-r border-gray-200 overflow-hidden"
      style={{ width: `${width}px`, minWidth: `${width}px` }}
    >
      {/* Sidebar Header */}
      <div className="flex-shrink-0 px-4 py-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-2">
          <FolderOpen className="w-5 h-5 text-gray-600" />
          <h2 className="font-semibold text-gray-800">Documents</h2>
          <div className="ml-auto px-2 py-0.5 bg-primary-100 text-primary-700 text-xs font-medium rounded-full">
            {uploadedFiles.length}
          </div>
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 space-y-4">
        {showUpload && (
          <div className="animate-slideUp">
            <FileUpload onUploadSuccess={onUploadSuccess} />
          </div>
        )}
        
        <FileList
          files={uploadedFiles}
          selectedFile={selectedFile}
          onSelectFile={onSelectFile}
          onDeleteFile={onDeleteFile}
          selectedDocumentIds={selectedDocumentIds}
          onToggleDocument={onToggleDocument}
        />
      </div>

      {/* Upload Toggle Footer */}
      <div className="flex-shrink-0 p-3 border-t border-gray-200 bg-gray-50">
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="w-full px-4 py-2 text-sm font-medium text-primary-600 bg-primary-50 hover:bg-primary-100 rounded-lg transition-colors duration-200"
        >
          {showUpload ? 'Hide Upload' : 'Upload Files'}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
