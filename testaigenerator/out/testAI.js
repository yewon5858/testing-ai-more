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
const vscode = __importStar(require("vscode"));
class TestAI extends vscode.WebviewPanel {
    text = '';
    constructor(panel, extensionUri) {
        super(panel, extensionUri, 'TestAI', {
            enableScripts: true,
        });
        this.panel.webview.html = this.getHtmlForWebview(extensionUri);
        this.panel.webview.onDidReceiveMessage((message) => {
            switch (message.command) {
                case 'alert':
                    vscode.window.showErrorMessage(message.text);
                    return;
                case 'run':
                    try {
                        const result = eval(message.code);
                        vscode.window.showInformationMessage(`Result: ${result}`);
                    }
                    catch (error) {
                        vscode.window.showErrorMessage(`Error: ${error.message}`);
                    }
                    return;
                case 'saveText':
                    this.text = message.text;
                    break;
            }
        }, undefined, this.disposables);
    }
    getHtmlForWebview(extensionUri) {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Test Generator</title>
        </head>
        <body>
            <h1>Test Generator</h1>
            <textarea id="input" rows="10" cols="50"></textarea>
            <button id="save">Save</button>
            <script>
                (function() {
                    const vscode = acquireVsCodeApi();
                    const input = document.getElementById('input');
                    const saveButton = document.getElementById('save');
                    saveButton.addEventListener('click', () => {
                        const code = input.value;
                        vscode.postMessage({
                            command: 'saveText',
                            text: code,
                        });
                    });
                })();
            </script>
        </body>
        </html>`;
    }
}
//# sourceMappingURL=testAI.js.map