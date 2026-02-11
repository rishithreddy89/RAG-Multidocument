/**
 * FileList Component
 * Display list of uploaded files with checkbox selection and delete
 */

import React from 'react';
import { File, FileText, Trash2 } from 'lucide-react';

const FileList = ({ files, selectedFile, onSelectFile, onDeleteFile, selectedDocumentIds, onToggleDocument }) => {
  const getFileIcon = (fileName) => {
    if (fileName.endsWith('.pdf')) {
      return <File className="w-5 h-5 text-red-500" />;
    }
    return <FileText className="w-5 h-5 text-blue-500" />;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  if (files.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full py-12 text-center">
        <div className="p-4 bg-gray-100 rounded-full mb-4">
          <File className="w-12 h-12 text-gray-400" />
        </div>
        <p className="text-gray-500 font-medium">No documents uploaded yet</p>
        <p className="text-sm text-gray-400 mt-1">Upload files to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="text-sm font-semibold text-gray-700 mb-3 px-1 flex items-center justify-between">
        <span>Documents ({files.length})</span>
        <span className="text-xs font-normal text-primary-600">
          {selectedDocumentIds.length} selected
        </span>
      </div>
      
      {files.map((file, index) => {
        const isSelected = selectedFile?.name === file.name;
        const isChecked = selectedDocumentIds.includes(file.documentId);
        
        return (
          <div
            key={index}
            className={`
              group relative flex items-center space-x-3 p-3 rounded-xl
              transition-all duration-200
              ${isSelected 
                ? 'bg-primary-50 border-2 border-primary-500 shadow-sm' 
                : 'bg-white border-2 border-gray-200 hover:border-primary-300 hover:shadow-sm'
              }
            `}
          >
            {/* Checkbox for document selection */}
            <input
              type="checkbox"
              checked={isChecked}
              onChange={(e) => {
                e.stopPropagation();
                onToggleDocument(file.documentId);
              }}
              className="w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 focus:ring-2 cursor-pointer"
            />
            
            <div 
              onClick={() => onSelectFile(file)}
              className="flex items-center space-x-3 flex-1 min-w-0 cursor-pointer"
            >
              <div className="flex-shrink-0">
                {getFileIcon(file.name)}
              </div>
              
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium truncate ${isSelected ? 'text-primary-700' : 'text-gray-700'}`}>
                  {file.name}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(file.size)}
                </p>
              </div>
            </div>

            <button
              onClick={(e) => {
                e.stopPropagation();
                onDeleteFile(file);
              }}
              className={`
                flex-shrink-0 p-1.5 rounded-lg transition-all
                ${isSelected ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}
                hover:bg-red-50 text-gray-400 hover:text-red-500
              `}
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
};

export default FileList;
