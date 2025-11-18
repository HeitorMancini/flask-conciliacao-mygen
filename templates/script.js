// ====== CONFIGURAÇÃO ======
const CONFIG = { // INFORMAÇÕES SENSÍVEIS
    baseURL: 'https://chat.int.bayer.com/api/v2',
    apiKey: 'mga-797f7606c1a9c4f7668a17dd7189f0f9873b31fd', 
    assistantId: 'db5a5273-9c09-48c9-837e-6d31e8490af9' 
};

// ====== CLIENTE myGenAssist ======
class MyGenAssistClient {
    constructor(baseURL, apiKey, assistantId) {
        this.baseURL = baseURL;
        this.apiKey = apiKey;
        this.assistantId = assistantId;
    }

    async sendMessage(messages, options = {}) {
        const payload = {
            messages: messages,
            assistant_id: this.assistantId,
            stream: options.stream || false,
            conversation_id: options.conversation_id,
            hidden: options.hidden || false,
            ...options
        };

        const response = await fetch(`${this.baseURL}/chat/agent`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-baychatgpt-accesstoken': this.apiKey
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Erro ${response.status}: ${errorText}`);
        }

        return response;
    }

    async getAssistantInfo() {
        const response = await fetch(`${this.baseURL}/assistants/${this.assistantId}`, {
            method: 'GET',
            headers: {
                'x-baychatgpt-accesstoken': this.apiKey
            }
        });

        if (!response.ok) {
            throw new Error(`Erro ao buscar assistente: ${response.status}`);
        }

        return response.json();
    }
}
