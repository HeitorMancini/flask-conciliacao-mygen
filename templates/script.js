const API_CONFIG = {
  BACKEND_URL: '/api/chat',
  API_URL: "{{ api_url }}",
  API_KEY: "{{ api_key }}",           // WARNING: don't expose this in production
  ASSISTANT_ID: "{{ assistant_id }}",
  // Safe parse for headers coming from template engine
  HEADERS: (() => {
    try {
      return JSON.parse(`{{ headers | tojson | safe }}`);
    } catch (err) {
      console.warn('Failed to parse HEADERS from template, using default headers', err);
      return { "Content-Type": "application/json" };
    }
  })()
};

class ChatBot {
  constructor() {
    // DOM elements
    this.chatMessages = document.getElementById('chatMessages');
    this.messageInput = document.getElementById('messageInput');
    this.sendButton = document.getElementById('sendButton');
    this.chatForm = document.getElementById('chatForm');

    // state
    this.conversationId = null;
    this.isProcessing = false;

    // event listeners
    if (this.sendButton) {
      this.sendButton.addEventListener('click', () => this.handleSendMessage());
    }
    if (this.messageInput) {
      this.messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !this.isProcessing) {
          e.preventDefault();
          this.handleSendMessage();
        }
      });
    }
  }

  async handleSendMessage() {
    // wrapper to call sendMessage with proper `this`
    await this.sendMessage();
  }

  async sendMessage() {
    const message = this.messageInput?.value?.trim();
    if (!message || this.isProcessing) return;

    // add user message to UI and clear input
    this.addMessage(message, 'user');
    this.messageInput.value = '';

    // start loading UI
    this.setLoading(true);
    this.isProcessing = true;

    try {
      // send to backend (Flask) for auxiliary processing / filters / context
      const backendResponse = await this.sendToBackend(message);

      if (backendResponse && backendResponse.error) {
        throw new Error(backendResponse.error);
      }

      // determine system context from backend response (if any)
      const systemContext = backendResponse?.context ?? '';

      // call AI agent
      const aiResponse = await this.sendToAIAgent(message, systemContext);

      // safe extraction of text from AI response (handle multiple possible shapes)
      const aiText =
        aiResponse?.content ||
        aiResponse?.message ||
        (Array.isArray(aiResponse?.messages) && aiResponse.messages[0]?.content) ||
        aiResponse?.output ||
        JSON.stringify(aiResponse);

      // show response
      this.addMessage(aiText, 'bot', backendResponse?.filters_found);

      // persist conversation id if backend returned one and we don't have it yet
      if (!this.conversationId && backendResponse?.conversation_id) {
        this.conversationId = backendResponse.conversation_id;
      }
      // or if AI returned a conversation id
      if (!this.conversationId && aiResponse?.conversation_id) {
        this.conversationId = aiResponse.conversation_id;
      }

    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      this.addErrorMessage(error?.message || 'Erro desconhecido');
    } finally {
      this.setLoading(false);
      this.isProcessing = false;
    }
  }

  // send message to your Flask backend (example: moderation, context generation, etc.)
  async sendToBackend(message) {
    const formData = new FormData();
    formData.append('message', message);
    // optionally append conversation id
    if (this.conversationId) formData.append('conversation_id', this.conversationId);

    const response = await fetch(API_CONFIG.BACKEND_URL, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      // try to parse error body if any
      let errBody = null;
      try { errBody = await response.json(); } catch (e) { /* ignore */ }
      throw new Error(`Erro no backend: ${response.status} ${errBody?.message ?? ''}`);
    }

    return await response.json();
  }

  // call MyGenAI (or equivalent) agent endpoint
  async sendToAIAgent(userMessage, systemContext) {
    const payload = {
      stream: false,
      hidden: true,
      assistant_id: API_CONFIG.ASSISTANT_ID,
      messages: [
        { role: "system", content: systemContext ?? "" },
        { role: "user", content: userMessage }
      ]
    };

    if (this.conversationId) {
      payload.conversation_id = this.conversationId;
    }

    // ensure headers exist and include content-type
    const headers = Object.assign({ "Content-Type": "application/json" }, API_CONFIG.HEADERS || {});

    const response = await fetch(`${API_CONFIG.API_URL}/chat/agent`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`Erro na API MyGenAI: ${response.status} - ${errorData.message || errorData.detail || 'Erro desconhecido'}`);
    }

    const data = await response.json();
    return data;
  }

  addMessage(text, sender, meta = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const avatar = sender === 'user' ? '👤' : '🤖';

    const contentHtml = this.formatMessage(String(text ?? ''));

    // optionally show meta (e.g., filters found)
    const metaHtml = meta ? `<div class="message-meta">${this.formatMessage(String(meta))}</div>` : '';

    messageDiv.innerHTML = `
      <div class="message-avatar">${avatar}</div>
      <div class="message-content">${contentHtml}${metaHtml}</div>
    `;

    this.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();
  }

  addErrorMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message error-message';
    messageDiv.innerHTML = `
      <div class="message-avatar">⚠️</div>
      <div class="message-content">${this.formatMessage(String(text))}</div>
    `;
    this.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();
  }

  formatMessage(text) {
    // convert newlines to <br> and escape basic HTML
    const escaped = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    return escaped.replace(/\n/g, '<br>');
  }

  setLoading(isLoading) {
    if (!this.sendButton) return;
    this.sendButton.disabled = isLoading;
    const sendText = this.sendButton.querySelector('.send-text');
    const loadingSpinner = this.sendButton.querySelector('.loading-spinner');

    if (sendText && loadingSpinner) {
      if (isLoading) {
        sendText.style.display = 'none';
        loadingSpinner.style.display = 'inline';
      } else {
        sendText.style.display = 'inline';
        loadingSpinner.style.display = 'none';
      }
    }
  }

  scrollToBottom() {
    setTimeout(() => {
      if (this.chatMessages) {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
      }
    }, 50);
  }
}

// initialize chatbot on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.chatBot = new ChatBot();
});