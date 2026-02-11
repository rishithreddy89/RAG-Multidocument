/**
 * MessageBubble Component
 * Individual chat message with styling
 */

import React from 'react';
import { User, Bot, AlertCircle } from 'lucide-react';

const MessageBubble = ({ message }) => {
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
    return (
      <div className="flex items-start space-x-3 animate-fadeIn">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
          <Bot className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1 bg-white border border-gray-200 rounded-2xl rounded-tl-none px-4 py-3 max-w-[80%] shadow-sm">
          <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">{content}</p>
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
