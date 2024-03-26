// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');
const { OpenAIClient, AzureKeyCredential } = require("@azure/openai");
require('dotenv').config(); // Load environment variables from .env file
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
const endpoint = process.env["AZURE_OPENAI_ENDPOINT"];
const azureApiKey = process.env["AZURE_OPENAI_API_KEY"];


async function generateTestCases(booleanExpression) {
    try {
        const messages = [
            { role: "system", content: "You are a helpful chatgpt." },
            { role: "user", content: "I need help with a conditional statement." },
            { role: "assistant", content: "Sure, what conditional statement are you working with?" },
            { role: "user", content: "Generate a set of test cases that satisfy the MC/DC coverage criterion for the following boolean expression." },
            { role: "assistant", content: "Sure, what boolean expresion are you working with?" },
            { role: "user", content: "With the following boolean expression:"+booleanExpression+"." },
            { role: "user", content: "Represent the solution as a list in Python, where each test case is a dictionary with the format {variable: value}" },
            { role: "user", content: "Respond with only the Python list, no explanations or extra text, just the requested list please." }
        ];
        console.log("== RESPUESTA DEL CHAT==");
        const client = new OpenAIClient(endpoint, new AzureKeyCredential(azureApiKey));
        const deploymentId = "generacion-de-casos";
        const result = await client.getChatCompletions(deploymentId, messages);

        for (const choice of result.choices) {
            vscode.window.showInformationMessage(choice.message.content);
        }
    } catch (error) {
        console.error('Error generating test cases:', error.message);
        vscode.window.showErrorMessage('Failed to generate test cases. See console for details.');
    }
}
/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "executeia" is now active!');
	let disposable = vscode.commands.registerCommand('executeia.EjecutarIA', () => {
        console.log('Activating executeia in azure folder...');
        const editor = vscode.window.activeTextEditor;
        if(!editor) {
            vscode.window.showErrorMessage('No hay ningún editor abierto.');
            return;
        }

        const expresion = editor.document.getText(editor.selection);
        if(!expresion)
        {
            vscode.window.showErrorMessage('No hay texto seleccionado.');
            return;
        }
		generateTestCases(expresion);
		
});

	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
function deactivate() {}

module.exports = {
	activate,
	deactivate
}
