"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
function activate(context) {
    context.subscriptions.push(vscode.commands.registerCommand('gotogpt.start', () => {
        // Create and show a new webview
        const panel = vscode.window.createWebviewPanel('chatgpt', // Identifies the type of the webview. Used internally
        'Chat gpt talking', // Title of the panel displayed to the user
        vscode.ViewColumn.One, // Editor column to show the new webview panel in.
        {
            enableScripts: true,
        } // Webview options. More on these later.
        );
        // Para tomar los mensajes producidos por la extensión
        panel.webview.onDidReceiveMessage(async (message) => {
            switch (message.command) {
                case 'userMessage':
                    const gptResponse = await sendToChatGPT(message.text);
                    panel.webview.postMessage({ command: 'gptResponse', text: gptResponse });
                    break;
            }
        }, undefined, context.subscriptions);
        panel.webview.html = getWebviewContent();
    }));
}
exports.activate = activate;
function getWebviewContent() {
    return `<!DOCTYPE html>
  <html lang="en">
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>ChatGPT</title>
  </head>
  <body>
    <div>
      <input type="text" id="userInput" placeholder="Type your message..."/>
      <button onclick="sendMessage()">Send</button>
    </div>
    <div id="chatHistory"></div>

    <script>
        const vscode = acquireVsCodeApi();

        function sendMessage() {
            const userInput = document.getElementById('userInput').value;
            if (userInput) {
                // Enviar el mensaje del usuario a la extensión de VS Code
                vscode.postMessage({ command: 'userMessage', text: userInput });
                // Limpiar el campo de entrada
                document.getElementById('userInput').value = '';
            }
        }

        // Escuchar respuestas de ChatGPT desde la extensión de VS Code
        window.addEventListener('message', (event) => {
            const chatHistory = document.getElementById('chatHistory');
            if (event.data.command === 'gptResponse') {
                // Agregar la respuesta de ChatGPT al historial de chat
                chatHistory.innerHTML += '<p>ChatGPT: ' + event.data.text + '</p>';
            }
        });
    </script>
  </body>
  </html>`;
}
async function sendToChatGPT(userMessage) {
    const apiKey = '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'; // Reemplaza con tu clave de API de OpenAI
    const endpoint = 'https://api.openai.com/v1/chat/completions';
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
    };
    // Construye el objeto payload con mensajes de sistema y usuario
    const payload = {
        messages: [
            { role: 'system', content: 'You are a helpful assistant designed to output JSON.' },
            { role: 'user', content: userMessage },
        ],
        response_format: { type: 'json_object' }, // Habilita el modo JSON
    };
    try {
        const response = await axios_1.default.post(endpoint, payload, { headers });
        return response.data.choices[0].message.content.text;
    }
    catch (error) {
        if (axios_1.default.isAxiosError(error)) {
            console.error('Error en la solicitud a la API de OpenAI:', error.message);
            console.error('Detalles del error:', error.response?.data);
        }
        throw error; // Re-lanzar el error para manejo adicional si es necesario
    }
}
//# sourceMappingURL=extension.js.map