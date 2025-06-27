import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { chatAPI } from '../services/api';
import MessageBubble from './MessageBubble';
import ProductCard from './ProductCard';

const ChatBot = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { user, logout } = useAuth();

  useEffect(() => {
    // Initial greeting
    setMessages([
      {
        id: 1,
        type: 'bot',
        content: {
          type: 'text',
          message: "Hello! I'm your shopping assistant. I can help you find laptops, smartphones, tablets, and accessories. What are you looking for today?",
          products: []
        },
        timestamp: new Date()
      }
    ]);

    // Load chat history
    loadChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      const history = await chatAPI.getChatHistory();
      if (history.length > 0) {
        const formattedHistory = history.reverse().map((item, index) => ([
          {
            id: `user-${index}`,
            type: 'user',
            content: { message: item.message },
            timestamp: new Date(item.timestamp.endsWith('Z') ? item.timestamp : item.timestamp + 'Z')

          },
          {
            id: `bot-${index}`,
            type: 'bot',
            content: item.response,
            timestamp: new Date(item.timestamp.endsWith('Z') ? item.timestamp : item.timestamp + 'Z')

          }
        ])).flat();
        
        setMessages(prev => [...prev, ...formattedHistory]);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: { message: inputMessage.trim() },
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage(inputMessage.trim());
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: {
          type: 'text',
          message: 'Sorry, I encountered an error. Please try again.',
          products: []
        },
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        type: 'bot',
        content: {
          type: 'text',
          message: "Chat cleared! How can I help you find products today?",
          products: []
        },
        timestamp: new Date()
      }
    ]);
  };

  const handleProductAction = (product, action) => {
    let message = '';
    switch (action) {
      case 'view':
        message = `Tell me more about the ${product.name}`;
        break;
      case 'compare':
        message = `Show me similar products to ${product.name}`;
        break;
      case 'buy':
        message = `I want to buy the ${product.name}`;
        break;
      default:
        return;
    }
    
    setInputMessage(message);
    setTimeout(() => sendMessage(), 100);
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <div className="header-info">
          <h2>Shopping Assistant</h2>
          <span className="user-info">Welcome, {user.username}!</span>
        </div>
        <div className="header-actions">
          <button onClick={clearChat} className="clear-btn">
            Clear Chat
          </button>
          <button onClick={logout} className="logout-btn">
            Logout
          </button>
        </div>
      </div>

      <div className="messages-container">
        {messages.map((message) => (
          <div key={message.id} className={`message-wrapper ${message.type}`}>
            <MessageBubble message={message} />
            {message.content.products && message.content.products.length > 0 && (
              <div className="products-grid">
                {message.content.products.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onAction={handleProductAction}
                  />
                ))}
              </div>
            )}
          </div>
        ))}
        
        {isTyping && (
          <div className="message-wrapper bot">
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <div className="input-wrapper">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about products... (e.g., 'Show me laptops under $1000')"
            disabled={loading}
            rows="1"
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || loading}
            className="send-btn"
          >
            Send
          </button>
        </div>
        <div className="quick-suggestions">
          <button onClick={() => setInputMessage("Show me laptop")}>
            Laptop
          </button>
          <button onClick={() => setInputMessage("I need a gaming laptop")}>
            Gaming laptops
          </button>
          <button onClick={() => setInputMessage("Show me iPhone models")}>
            iPhone models
          </button>
          <button onClick={() => setInputMessage(" Show me headphones")}>
            Headphones
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatBot;