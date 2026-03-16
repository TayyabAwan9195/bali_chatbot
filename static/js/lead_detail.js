// static/js/lead_detail.js - Lead detail page functionality

class LeadDetailApp {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.scrollChatToBottom();
        this.formatPhoneNumbers();
    }

    bindEvents() {
        // Category change
        const categorySelect = document.getElementById('categorySelect');
        if (categorySelect) {
            categorySelect.addEventListener('change', (e) => this.changeCategory(e.target.value));
        }

        // Send message form
        const messageForm = document.getElementById('messageForm');
        if (messageForm) {
            messageForm.addEventListener('submit', (e) => this.sendMessage(e));
        }

        // Auto-resize textarea
        const textarea = document.getElementById('messageTextarea');
        if (textarea) {
            textarea.addEventListener('input', () => this.autoResizeTextarea(textarea));
        }
    }

    formatPhoneNumbers() {
        // Format phone numbers throughout the page
        const phoneElements = document.querySelectorAll('.phone-number');
        phoneElements.forEach(element => {
            const phone = element.textContent;
            element.textContent = this.formatPhoneNumber(phone);
        });
    }

    formatPhoneNumber(phone) {
        if (!phone) return phone;
        // Remove whatsapp: prefix and ensure + format
        return phone.replace(/^whatsapp:/, '').replace(/^\+?/, '+');
    }

    async changeCategory(newCategory) {
        const leadId = document.getElementById('leadId')?.value;
        if (!leadId) return;

        try {
            const response = await fetch(`/admin/change_category/${leadId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ category: newCategory })
            });

            if (response.ok) {
                // Update the badge
                const badge = document.querySelector('.category-badge');
                if (badge) {
                    badge.className = `category-badge badge-${newCategory.toLowerCase()}`;
                    badge.textContent = newCategory.toUpperCase();
                }
                this.showNotification('Category updated successfully', 'success');
            } else {
                throw new Error('Failed to update category');
            }
        } catch (error) {
            console.error('Error changing category:', error);
            this.showNotification('Failed to update category', 'error');
        }
    }

    async sendMessage(event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const message = formData.get('message')?.trim();

        if (!message) {
            this.showNotification('Please enter a message', 'error');
            return;
        }

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending...';

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                // Add the message to chat
                this.addMessageToChat('user', message);

                // Clear the form
                form.reset();

                // Reset textarea height
                const textarea = document.getElementById('messageTextarea');
                if (textarea) {
                    textarea.style.height = 'auto';
                }

                this.showNotification('Message sent successfully', 'success');
            } else {
                throw new Error('Failed to send message');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.showNotification('Failed to send message', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    addMessageToChat(type, content) {
        const chatMessages = document.getElementById('chatMessages');
        if (!chatMessages) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = content;

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = this.getCurrentTime();

        messageDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(timeDiv);
        chatMessages.appendChild(messageDiv);

        this.scrollChatToBottom();
    }

    scrollChatToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            setTimeout(() => {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 100);
        }
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : 'success'} notification`;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            padding: 12px 16px;
            border-radius: 6px;
            color: white;
            background-color: ${type === 'error' ? '#dc3545' : '#28a745'};
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            max-width: 300px;
            opacity: 0;
            transform: translateY(-20px);
            transition: all 0.3s ease;
        `;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 100);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-20px)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Initialize lead detail app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LeadDetailApp();
});