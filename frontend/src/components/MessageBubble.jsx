/**
 * MessageBubble Component
 * Individual chat message with styling
 */

import React from 'react';
import { User, Bot, AlertCircle } from 'lucide-react';

const MessageBubble = ({ message, onHighlightClick }) => {
  const { role, content } = message;

  if (role === 'user') {
    return (
      <div className="flex items-start space-x-3 animate-fadeIn">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1 bg-primary-50 rounded-2xl rounded-tl-none px-4 py-3 max-w-[80%]">
          <p className="text-sm text-gray-800 whitespace-pre-wrap">{content}</p>
        </div>
      </div>
    );
  }

  if (role === 'assistant') {
    const highlights = Array.isArray(message.highlights) ? message.highlights : [];
    return (
      <div className="flex items-start space-x-3 animate-fadeIn">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
          <Bot className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1 bg-white border border-gray-200 rounded-2xl rounded-tl-none px-4 py-3 max-w-[80%] shadow-sm">
          <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">{content}</p>

          {highlights.length > 0 && (
            <div className="mt-4 pt-3 border-t border-gray-100">
              <p className="text-xs font-semibold text-gray-500 mb-2">Sources</p>
              <div className="space-y-2">
                {highlights.map((h, idx) => (
                  <button
                    key={`${h.doc_name || 'doc'}-${h.page || 1}-${idx}`}
                    onClick={() => onHighlightClick && onHighlightClick(h)}
                    className="w-full text-left px-3 py-2 rounded-lg bg-amber-50 hover:bg-amber-100 border border-amber-200 transition-colors"
                    title="Jump to highlighted evidence"
                  >
                    <p className="text-xs font-medium text-amber-900">
                      {h.doc_name || 'Unknown'} (Page {h.page || 1})
                    </p>
                    <p className="text-xs text-amber-800 mt-1 line-clamp-2">{h.text}</p>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (role === 'error') {
    return (
      <div className="flex items-start space-x-3 animate-fadeIn">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-red-100 flex items-center justify-center">
          <AlertCircle className="w-5 h-5 text-red-500" />
        </div>
        <div className="flex-1 bg-red-50 border border-red-200 rounded-2xl rounded-tl-none px-4 py-3 max-w-[80%]">
          <p className="text-sm text-red-700 whitespace-pre-wrap">{content}</p>
        </div>
      </div>
    );
  }

  return null;
};

export default MessageBubble;
