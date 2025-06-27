import React from 'react';

const MessageBubble = ({ message }) => {
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const renderMessageContent = () => {
    if (message.type === 'user') {
      return <p>{message.content.message}</p>;
    }

    // Bot message
    const content = message.content;
    
    return (
      <div>
        <p>{content.message}</p>
        
        {content.suggestions && content.suggestions.length > 0 && (
          <div className="suggestions">
            <p><strong>Suggestions:</strong></p>
            <ul>
              {content.suggestions.map((suggestion, index) => (
                <li key={index}>{suggestion}</li>
              ))}
            </ul>
          </div>
        )}
        
        {content.filters && (
          <div className="filters-info">
            <p><em>Applied filters: {JSON.stringify(content.filters)}</em></p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`message-bubble ${message.type}`}>
      <div className="message-content">
        {renderMessageContent()}
      </div>
      <div className="message-time">
        {formatTime(message.timestamp)}
      </div>
    </div>
  );
};

export default MessageBubble;