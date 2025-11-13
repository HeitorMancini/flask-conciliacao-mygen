class ChatBot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatForm = document.getElementById('chatForm');
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        this.chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Adiciona mensagem do usuário
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        
        // Mostra loading
        this.setLoading(true);
        
        try {
            const formData = new FormData;
            formData.append('message', message);
            
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            this.addMessage(data.response, 'bot');

        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            this.addMessage('Desculpe, ocorreu um erro. Tente novamente.', 'bot');
        } finally {
            this.setLoading(false);
        }
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = sender === 'user' ? '👤' : '🤖';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">${this.formatMessage(text)}</div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(text) {
        // Converte quebras de linha em <br>
        return text.replace(/\n/g, '<br>');
    }
    
    setLoading(isLoading) {
        this.sendButton.disabled = isLoading;
        const sendText = this.sendButton.querySelector('.send-text');
        const loadingSpinner = this.sendButton.querySelector('.loading-spinner');
        
        if (isLoading) {
            sendText.style.display = 'none';
            loadingSpinner.style.display = 'inline';
        } else {
            sendText.style.display = 'inline';
            loadingSpinner.style.display = 'none';
        }
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
}

// Inicializa o chatbot quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
    new ChatBot();
});