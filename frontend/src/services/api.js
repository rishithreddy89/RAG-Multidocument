/**
 * API service for communicating with FastAPI backend.
 */

import axios from 'axios';

// Backend API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetch all uploaded documents.
 * @returns {Promise<Object>} - List of documents
 */
export const fetchDocuments = async () => {
  try {
    const response = await apiClient.get('/upload/documents');
    return response.data;
  } catch (error) {
    console.error('Error fetching documents:', error);
    throw error;
  }
};

/**
 * Delete a document by ID.
 * @param {string} documentId - Document ID to delete
 * @returns {Promise<Object>} - Deletion confirmation
 */
export const deleteDocument = async (documentId) => {
  try {
    const response = await apiClient.delete(`/upload/documents/${documentId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting document:', error);
    throw error;
  }
};

/**
 * Fetch chat history.
 * @returns {Promise<Object>} - Chat history
 */
export const fetchChatHistory = async () => {
  try {
    const response = await apiClient.get('/chat/history');
    return response.data;
  } catch (error) {
    console.error('Error fetching chat history:', error);
    throw error;
  }
};

/**
 * Clear chat history.
 * @returns {Promise<Object>} - Confirmation
 */
export const clearChatHistory = async () => {
  try {
    const response = await apiClient.delete('/chat/history');
    return response.data;
  } catch (error) {
    console.error('Error clearing chat history:', error);
    throw error;
  }
};

/**
 * Send a message to the chat endpoint with selected documents.
 * 
 * @param {string} message - User's question or message
 * @param {Array<string>} selectedDocuments - Array of document IDs to query
 * @returns {Promise<string>} - LLM response
 * @throws {Error} - If API request fails
 */
export const sendChatMessage = async (message, selectedDocuments = []) => {
  try {
    const response = await apiClient.post('/chat', { 
      message,
      selected_documents: selectedDocuments
    });
    return response.data.response;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Failed to get response from LLM');
    } else if (error.request) {
      throw new Error('Cannot connect to backend. Make sure the server is running.');
    } else {
      throw new Error('An unexpected error occurred');
    }
  }
};

/**
 * Upload multiple documents to the backend.
 * 
 * Phase 2 TODO: Documents will be automatically processed and indexed in ChromaDB
 * 
 * @param {FileList} files - Files to upload
 * @returns {Promise<Object>} - Upload response with file names and message
 * @throws {Error} - If upload fails
 */
export const uploadDocuments = async (files) => {
  try {
    const formData = new FormData();
    
    // Add all files to form data
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });
    
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Failed to upload documents');
    } else if (error.request) {
      throw new Error('Cannot connect to backend. Make sure the server is running.');
    } else {
      throw new Error('An unexpected error occurred during upload');
    }
  }
};

export default apiClient;
