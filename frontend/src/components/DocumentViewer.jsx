/**
 * DocumentViewer Component
 * Router for PDF and Text viewers based on file type
 */

import React from 'react';
import PDFViewer from './PDFViewer';
import TextViewer from './TextViewer';
import { FileQuestion } from 'lucide-react';

const DocumentViewer = ({ file }) => {
  if (!file) {
    return (
      <div className="flex flex-col items-center justify-center h-full bg-gray-50">
        <div className="p-6 bg-white rounded-2xl shadow-sm">
          <FileQuestion className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 font-medium">No document selected</p>
          <p className="text-sm text-gray-400 mt-1">Select a file to view</p>
        </div>
      </div>
    );
  }

  const isPDF = file.name.toLowerCase().endsWith('.pdf');
  const isTXT = file.name.toLowerCase().endsWith('.txt');

  if (isPDF) {
    return <PDFViewer file={file} />;
  } else if (isTXT) {
    return <TextViewer file={file} />;
  }

  return (
    <div className="flex items-center justify-center h-full bg-gray-50">
      <div className="text-center">
        <FileQuestion className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500 font-medium">Unsupported file type</p>
        <p className="text-sm text-gray-400 mt-1">Only PDF and TXT files are supported</p>
      </div>
    </div>
  );
};

export default DocumentViewer;
