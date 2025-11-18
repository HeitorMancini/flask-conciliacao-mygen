// ====== CLIENTE myGenAssist ======
class MyGenAssistClient {
    constructor(baseURL, apiKey, assistantId) {
        this.baseURL = baseURL;
        this.apiKey = apiKey;
        this.assistantId = assistantId;
    }

    async sendMessage(messages, options = {}) {
        const payload = {
            assistant_id: ,
            conversation_id: conversation_id,
            stream: false,
            hidden: true,
            messages: [
                {
                    role: "system"
                    content: sys_msg
                },
                {
                    role: "user",
                    content: message
                }
            ]
        };

        const response = await fetch(`${this.baseURL}/chat/agent`, {
            method: 'POST',
            headers: {
                'Content-Type': 'applications/json',
                'x-baychatgpt-accesstoken': this.api_key
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
