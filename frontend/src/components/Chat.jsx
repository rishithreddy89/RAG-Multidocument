/**
 * Chat component for interacting with the LLM.
 * Phase 1: Direct chat with Qwen-2.5
 * Phase 2: Will include RAG with document context
 */

import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../services/api';
import './Chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /**
   * Handle sending a message to the LLM.
   */
  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      // Get response from backend
      const response = await sendChatMessage(userMessage);
      
      // Add assistant response to chat
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    } catch (error) {
      // Show error message in chat
      setMessages(prev => [
        ...prev,
        { role: 'error', content: `Error: ${error.message}` }
      ]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle Enter key press to send message.
   */
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>💬 Chat with LLM</h2>
        <p className="chat-subtitle">
          Phase 1: Direct chat | Phase 2: RAG-powered responses
        </p>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>👋 Start a conversation!</p>
            <p className="empty-hint">Ask me anything...</p>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-role">
              {msg.role === 'user' ? '👤 You' : msg.role === 'error' ? '⚠️ Error' : '🤖 Assistant'}
            </div>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}

        {loading && (
          <div className="message assistant loading">
            <div className="message-role">🤖 Assistant</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          rows="3"
          disabled={loading}
        />
        <button
          className="send-button"
          onClick={handleSend}
          disabled={!input.trim() || loading}
        >
          {loading ? '⏳ Sending...' : '📤 Send'}
        </button>
      </div>
    </div>
  );
};

export default Chat;
