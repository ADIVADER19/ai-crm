import React, { useState, useEffect, useRef } from 'react';
import { chatAPI, resetAPI, uploadAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import './Chat.css';

const Chat = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState('');
  const [showUpload, setShowUpload] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    setMessages([
      {
        role: 'assistant',
        content: `Hello ${user?.name || 'there'}! I'm your RentRadar assistant. I can help you find properties based on your preferences. What would you like to know about?`,
        timestamp: new Date().toISOString()
      }
    ]);
  }, [user]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);
    setError('');

    try {
      const response = await chatAPI.sendMessage(inputMessage);
      
      const assistantMessage = {
        role: 'assistant',
        content: response.reply,
        timestamp: new Date().toISOString(),
        category: response.category,
        response_time: response.response_time_ms
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      setError('Failed to send message. Please try again.');
      console.error('Chat error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      await resetAPI.reset();
      setMessages([
        {
          role: 'assistant',
          content: `Hello ${user?.name || 'there'}! I'm your RentRadar assistant. I can help you find properties based on your preferences. What would you like to know about?`,
          timestamp: new Date().toISOString()
        }
      ]);
    } catch (error) {
      setError('Failed to reset conversation');
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadLoading(true);
    setError('');
    setUploadSuccess('');

    try {
      const response = await uploadAPI.uploadDocs(file);
      setUploadSuccess(`Successfully uploaded ${response.inserted_count} documents. The AI now has updated context!`);
      
      const systemMessage = {
        role: 'assistant',
        content: `📁 **Knowledge Base Updated!**\n\nI've successfully processed your uploaded file (${response.file_type.toUpperCase()}) with ${response.inserted_count} documents. My knowledge base is now updated with this new information. You can ask me questions about the content you just uploaded!`,
        timestamp: new Date().toISOString(),
        category: 'system_update'
      };
      setMessages(prev => [...prev, systemMessage]);
      
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      setShowUpload(false);
      
    } catch (error) {
      setError(`Upload failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploadLoading(false);
    }
  };

  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const formatMessage = (content, role) => {
    return content.split('\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        {index < content.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>RentRadar Chat</h1>
        <div className="header-actions">
          <button 
            onClick={() => setShowUpload(!showUpload)} 
            className="upload-toggle-button"
            disabled={uploadLoading}
          >
            📁 Upload Docs
          </button>
          <button onClick={handleReset} className="reset-button">
            🔄 Reset Chat
          </button>
        </div>
      </div>

      {showUpload && (
        <div className="upload-section">
          <div className="upload-content">
            <h3>📤 Upload Knowledge Base Documents</h3>
            <p>Upload PDF, TXT, CSV, or JSON files to provide context for the AI assistant.</p>
            
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.csv,.json"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
            
            <div className="upload-area">
              <button 
                onClick={handleUploadClick}
                className="upload-button"
                disabled={uploadLoading}
              >
                {uploadLoading ? (
                  <>
                    <span className="loading-spinner"></span>
                    Uploading...
                  </>
                ) : (
                  <>
                    Choose File
                  </>
                )}
              </button>
              
              <div className="upload-info">
                <p>Supported formats: PDF, TXT, CSV, JSON</p>
                <p>The uploaded file will replace the current knowledge base.</p>
              </div>
            </div>

            {uploadSuccess && (
              <div className="upload-success">
                ✅ {uploadSuccess}
              </div>
            )}
          </div>
        </div>
      )}

      <div className="chat-messages">
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
          >
            <div className="message-content">
              {formatMessage(message.content, message.role)}
            </div>
            <div className="message-meta">
              <span className="message-time">
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
              {message.category && (
                <span className="message-category">
                  {message.category.replace('_', ' ')}
                </span>
              )}
              {message.response_time && (
                <span className="response-time">
                  {Math.round(message.response_time)}ms
                </span>
              )}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="message assistant-message">
            <div className="message-content typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="chat-error">
          {error}
        </div>
      )}

      <form onSubmit={handleSendMessage} className="chat-input-form">
        <div className="input-container">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask me about properties, pricing, or anything else..."
            className="chat-input"
            disabled={loading}
          />
          <button 
            type="submit" 
            className="send-button"
            disabled={loading || !inputMessage.trim()}
          >
            📤
          </button>
        </div>
      </form>

      <div className="chat-suggestions">
        <p>Try asking:</p>
        <div className="suggestion-chips">
          <button 
            onClick={() => setInputMessage("Show me properties under $100,000 per month")}
            className="suggestion-chip"
          >
            Properties under $100k
          </button>
          <button 
            onClick={() => setInputMessage("What's the average price per square foot in Times Square?")}
            className="suggestion-chip"
          >
            Times Square pricing
          </button>
          <button 
            onClick={() => setInputMessage("Show me retail spaces in Manhattan")}
            className="suggestion-chip"
          >
            Manhattan retail spaces
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
