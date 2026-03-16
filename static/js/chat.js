// static/js/chat.js - Chat interface functionality

class ChatApp {
    constructor() {
        this.currentPhone = '';
        this.isTyping = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.scrollToBottom();
        this.loadInitialPhone();
    }

    bindEvents() {
        // Send message on form submit
        const form = document.getElementById('messageForm');
        if (form) {
            form.addEventListener('submit', (e) => this.sendMessage(e));
        }

        // Send message on Enter key
        const input = document.getElementById('messageInput');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage(e);
                }
            });
        }

        // Phone number input
        const phoneInput = document.getElementById('phoneInput');
        const setPhoneBtn = document.getElementById('setPhoneBtn');
        if (setPhoneBtn) {
            setPhoneBtn.addEventListener('click', () => this.setPhone());
        }
        if (phoneInput) {
            phoneInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.setPhone();
                }
            });
        }
    }

    loadInitialPhone() {
        const phoneInput = document.getElementById('phoneInput');
        if (phoneInput && phoneInput.value) {
            this.currentPhone = phoneInput.value;
        }
    }

    setPhone() {
        const phoneInput = document.getElementById('phoneInput');
        if (phoneInput) {
            this.currentPhone = phoneInput.value.trim();
            if (this.currentPhone) {
                this.showNotification(`Phone set to: ${this.currentPhone}`, 'success');
            } else {
                this.showNotification('Please enter a valid phone number', 'error');
            }
        }
    }

    async sendMessage(event) {
        event.preventDefault();

        const input = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const message = input.value.trim();

        if (!message) return;
        if (!this.currentPhone) {
            this.showNotification('Please set a phone number first', 'error');
            return;
        }

        // Disable input while sending
        input.disabled = true;
        sendBtn.disabled = true;

        // Add user message
        this.addMessage('user', message);
        input.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch('/test_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    phone: this.currentPhone,
                    message: message
                })
            });

            const data = await response.json();

            // Hide typing indicator
            this.hideTypingIndicator();

            // Add bot response
            this.addMessage('bot', data.response);

        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.showNotification('Failed to send message. Please try again.', 'error');
        } finally {
            // Re-enable input
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
    }

    addMessage(type, text) {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = text;

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = this.getCurrentTime();

        messageDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(timeDiv);
        messagesContainer.appendChild(messageDiv);

        this.scrollToBottom();
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer || this.isTyping) return;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.id = 'typingIndicator';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'typing-indicator';

        const dotsDiv = document.createElement('div');
        dotsDiv.className = 'typing-dots';

        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            dotsDiv.appendChild(dot);
        }

        bubbleDiv.appendChild(dotsDiv);
        typingDiv.appendChild(bubbleDiv);
        messagesContainer.appendChild(typingDiv);

        this.isTyping = true;
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingDiv = document.getElementById('typingIndicator');
        if (typingDiv) {
            typingDiv.remove();
        }
        this.isTyping = false;
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        if (messagesContainer) {
            setTimeout(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 100);
        }
    }

    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    showNotification(message, type = 'info') {
        // Simple notification - you can enhance this with a proper notification system
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : 'success'}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            padding: 12px 16px;
            border-radius: 6px;
            color: white;
            background-color: ${type === 'error' ? '#dc3545' : '#28a745'};
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 300px;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Initialize chat app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});