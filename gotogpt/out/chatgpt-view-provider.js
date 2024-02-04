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
Object.defineProperty(exports, "__esModule", { value: true });
const openai_1 = require("openai");
const vscode = __importStar(require("vscode"));
class ChatGptViewProvider {
    context;
    webView;
    openAiApi;
    apiKey;
    message;
    constructor(context) {
        this.context = context;
    }
    resolveWebviewView(webviewView, _context, _token) {
        this.webView = webviewView;
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.context.extensionUri]
        };
        webviewView.webview.html = this.getHtml(webviewView.webview);
        webviewView.webview.onDidReceiveMessage(data => {
            if (data.type === 'askChatGPT') {
                this.sendOpenAiApiRequest(data.value);
            }
        });
        if (this.message !== null) {
            this.sendMessageToWebView(this.message);
            this.message = null;
        }
    }
    async ensureApiKey() {
        this.apiKey = await this.context.globalState.get('chatgpt-api-key');
        if (!this.apiKey) {
            const apiKeyInput = await vscode.window.showInputBox({
                prompt: "Please enter your OpenAI API Key, can be located at https://openai.com/account/api-keys",
                ignoreFocusOut: true,
            });
            this.apiKey = apiKeyInput;
            this.context.globalState.update('chatgpt-api-key', this.apiKey);
        }
    }
    async sendOpenAiApiRequest(prompt, code) {
        await this.ensureApiKey();
        if (!this.openAiApi) {
            try {
                this.openAiApi = new openai_1.OpenAIApi(new openai_1.Configuration({ apiKey: this.apiKey }));
            }
            catch (error) {
                vscode.window.showErrorMessage("Failed to connect to ChatGPT", error?.message);
                return;
            }
        }
        // Create question by adding prompt prefix to code, if provided
        const question = (code) ? `${prompt}: ${code}` : prompt;
        if (!this.webView) {
            await vscode.commands.executeCommand('chatgpt-vscode-plugin.view.focus');
        }
        else {
            this.webView?.show?.(true);
        }
        let response = '';
        this.sendMessageToWebView({ type: 'addQuestion', value: prompt, code });
        try {
            let currentMessageNumber = this.message;
            let completion;
            try {
                completion = await this.openAiApi.createCompletion({
                    model: 'code-davinci-003',
                    prompt: question,
                    temperature: 0.5,
                    max_tokens: 2048,
                    stop: ['\n\n\n', '<|im_end|>'],
                });
            }
            catch (error) {
                await vscode.window.showErrorMessage("Error sending request to ChatGPT", error);
                return;
            }
            if (this.message !== currentMessageNumber) {
                return;
            }
            response = completion?.data.choices[0].text || '';
            const REGEX_CODEBLOCK = new RegExp('\`\`\`', 'g');
            const matches = response.match(REGEX_CODEBLOCK);
            const count = matches ? matches.length : 0;
            if (count % 2 !== 0) {
                response += '\n\`\`\`';
            }
            this.sendMessageToWebView({ type: 'addResponse', value: response });
        }
        catch (error) {
            await vscode.window.showErrorMessage("Error sending request to ChatGPT", error);
            return;
        }
    }
    sendMessageToWebView(message) {
        if (this.webView) {
            this.webView?.webview.postMessage(message);
        }
        else {
            this.message = message;
        }
    }
    getHtml(webview) {
        const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this.context.extensionUri, 'media', 'main.js'));
        const stylesMainUri = webview.asWebviewUri(vscode.Uri.joinPath(this.context.extensionUri, 'media', 'main.css'));
        return `<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				<link href="${stylesMainUri}" rel="stylesheet">
				<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
				<script src="https://cdn.tailwindcss.com"></script>
			</head>
			<body class="overflow-hidden">
				<div class="flex flex-col h-screen">
					<div class="flex-1 overflow-y-auto" id="qa-list"></div>
					<div id="in-progress" class="p-4 flex items-center hidden">
                        <div style="text-align: center;">
                            <div>Please wait while we handle your request ❤️</div>
                            <div class="loader"></div>
                            <div>Please note, ChatGPT facing scaling issues which will impact this extension</div>
                        </div>
					</div>
					<div class="p-4 flex items-center">
						<div class="flex-1">
							<textarea
								type="text"
								rows="2"
								class="border p-2 w-full"
								id="question-input"
								placeholder="Ask a question..."
							></textarea>
						</div>
						<button style="background: var(--vscode-button-background)" id="ask-button" class="p-2 ml-5">Ask</button>
						<button style="background: var(--vscode-button-background)" id="clear-button" class="p-2 ml-3">Clear</button>
					</div>
				</div>
				<script src="${scriptUri}"></script>
			</body>
			</html>`;
    }
}
exports.default = ChatGptViewProvider;
//# sourceMappingURL=chatgpt-view-provider.js.map