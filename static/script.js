document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const chatBox = document.getElementById('chat-box');
  const userInput = document.getElementById('user-input');
  const sendButton = document.getElementById('send-button');
  const typingIndicator = document.getElementById('typing-indicator');
  
  // Initial welcome message
  addMessage('GuBot', 'Hello! I\'m GuBot, your AI assistant. How can I help you today?', 'bot-message');
  
  // Event Listeners
  sendButton.addEventListener('click', sendMessage);
  userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
  });
  
  // Focus input on load
  userInput.focus();
  
  // Main Functions
  async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;
    
    // Add user message
    addMessage('You', message, 'user-message');
    userInput.value = '';
    disableInput();
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      addMessage('GuBot', data.reply, 'bot-message');
      
    } catch (error) {
      console.error('Error:', error);
      addMessage('System', 'Sorry, I encountered an error. Please try again.', 'error-message');
    } finally {
      hideTypingIndicator();
      enableInput();
      scrollToBottom();
    }
  }
  
  // Helper Functions
  function addMessage(sender, text, className) {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${className}`;
    messageElement.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatBox.appendChild(messageElement);
    scrollToBottom();
  }
  
  function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    scrollToBottom();
  }
  
  function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
  }
  
  function disableInput() {
    userInput.disabled = true;
    sendButton.disabled = true;
  }
  
  function enableInput() {
    userInput.disabled = false;
    sendButton.disabled = false;
    userInput.focus();
  }
  
  function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
  }
  
  // Optional: Add click-to-copy functionality
  chatBox.addEventListener('click', (e) => {
    if (e.target.classList.contains('message')) {
      const text = e.target.innerText.replace(/^\w+:\s/, '');
      navigator.clipboard.writeText(text).then(() => {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = 'Copied to clipboard!';
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 2000);
      });
    }
  });
});
  
