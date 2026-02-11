/**
 * ChatPanel Component
 * Collapsible chat interface with toggle button
 */

import React from 'react';
import { MessageSquare, ChevronRight, ChevronLeft } from 'lucide-react';
import ChatWindow from './ChatWindow';

const ChatPanel = ({ 
  width, 
  isCollapsed, 
  onToggleCollapse,
  isHidden,
  initialMessages = [],
  isLoadingState = false,
  selectedDocumentIds = []
}) => {
  if (isHidden) return null;

  if (isCollapsed) {
    return (
      <div className="flex flex-col items-center bg-white border-l border-gray-200 w-12 flex-shrink-0">
        <button
          onClick={onToggleCollapse}
          className="w-full p-3 text-gray-600 hover:bg-primary-50 hover:text-primary-600 transition-colors duration-200 border-b border-gray-200"
          title="Expand Chat"
        >
          <ChevronLeft className="w-6 h-6 mx-auto" />
        </button>
        <div className="flex-1 flex items-center justify-center">
          <div className="writing-vertical-rl transform rotate-180">
            <span className="text-sm font-medium text-gray-500">Chat</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className="flex flex-col bg-white border-l border-gray-200 overflow-hidden transition-all duration-300"
      style={{ width: `${width}px`, minWidth: `${width}px` }}
    >
      {/* Chat Header with Collapse Button */}
      <div className="flex-shrink-0 flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center space-x-2">
          <MessageSquare className="w-5 h-5 text-gray-600" />
          <h2 className="font-semibold text-gray-800">AI Chat</h2>
        </div>
        <button
          onClick={onToggleCollapse}
          className="p-1.5 text-gray-600 hover:bg-gray-200 rounded-lg transition-colors duration-200"
          title="Collapse Chat"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Chat Content */}
      <div className="flex-1 overflow-hidden">
        <ChatWindow 
          initialMessages={initialMessages}
          isLoadingState={isLoadingState}
          selectedDocumentIds={selectedDocumentIds}
        />
      </div>
    </div>
  );
};

export default ChatPanel;
