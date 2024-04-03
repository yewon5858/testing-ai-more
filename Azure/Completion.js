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
    // ingles o en español?
    try {
        const messages = [
            { role: "system", content: "You are an expert generating test cases that satisfy the MC/DC coverage criterion." },
            { role: "user", content: "I need help with test case generation, that satisfy the MC/DC coverage criterion" },
            { role: "assistant", content: "Okay, I'm an expert in that criterion. Tell me what I need to do ?" },
            { role: "user", content: "I provide you an example, in this case the boolean expression is (a<10)&(b<9)." },
            { role: "user", content: "And the output I get is in the style [{a: 0, b: 0}, {a: 11, b: 0}, {a: 11, b: 9}]." },
            { role: "user", content: "Giving you boolean expressions, can you provide me with responses in the same style as the one I just showed you?" },        
            { role: "assistant", content: "Of course! What type of test cases are you trying to generate?" },
            { role: "user", content: "I want to generate the minimum test cases that satisfy the MC/DC coverage criterion for a boolean expression." },
            { role: "assistant", content: "Understood. Please provide the boolean expression for which you want to generate test cases." },
            { role: "user", content: "The boolean expression is as follows: "+booleanExpression+"." },
            { role: "user", content: "Respond with only the Python list, no explanations or extra text, just the requested list please." }
        ];
        console.log("== RESPUESTA DEL CHAT==");
        const client = new OpenAIClient(endpoint, new AzureKeyCredential(azureApiKey));
        const deploymentId = "generacion-de-casos";
        const result = await client.getChatCompletions(deploymentId, messages);
        // desplegable en la ventana creada 
        for (const choice of result.choices) {
            vscode.window.showInformationMessage(choice.message.content);
        }

        // Mostrar la lista de valores de prueba en la consola
        const testCasesMessage = result.choices[result.choices.length - 1].message.content
        console.log(testCasesMessage);
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
