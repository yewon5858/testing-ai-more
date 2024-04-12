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
exports.deactivate = exports.activate = void 0;
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const { OpenAIClient, AzureKeyCredential } = require("@azure/openai");
async function readConfig() {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('No se encontraron carpetas en el espacio de trabajo.');
        throw new Error('No se encontraron carpetas en el espacio de trabajo.');
    }
    const workspaceFolder = workspaceFolders[0];
    const parentFolder = vscode.Uri.joinPath(workspaceFolder.uri, '../'); //Directorio padre
    const configFilePath = vscode.Uri.joinPath(parentFolder, 'config.json');
    //Read config.json
    console.log(configFilePath); // Agregar esta línea para verificar la ruta
    try {
        const data = await fs.promises.readFile(configFilePath.fsPath, 'utf8');
        const configDetails = JSON.parse(data);
        return configDetails;
    }
    catch (error) {
        vscode.window.showErrorMessage('Error al leer o parsear el archivo de configuración.');
        throw new Error('Error al leer o parsear el archivo de configuración.');
    }
}
//PYENV------------------------------------------------------------------------------
let twsl;
//Ejecutar py-MCDC + argumento
function run_exec(context, eq) {
    // Ejecutar el script Python en el terminal
    twsl.sendText(`python exec.py ` + eq);
}
//Prepare terminal and environment
function prepareEnvironment(configDetails) {
    try {
        //Create pyenv environment
        twsl = vscode.window.createTerminal({
            name: configDetails.terminalName, //Name of the terminal
            shellPath: configDetails.shellPath, //WSL
            shellArgs: [],
        });
        twsl.show();
        twsl.sendText(configDetails.pyenvActivation);
        twsl.sendText(`cd ${configDetails.directoryPath}`);
        twsl.sendText('clear');
        //Environment ready to use
        vscode.window.showInformationMessage(`Entorno preparado, no cerrar el terminal ${twsl.name}`);
    }
    catch {
        vscode.window.showInformationMessage('Error al preparar el entorno');
    }
}
//LLMs-----------------------------------------------------------------------------------
async function generateTestCases(configDetails, eq) {
    try {
        const endpoint = configDetails.endpoint;
        const azureApiKey = configDetails.apiKey;
        const messages = [
            { role: "system", content: "You are a helpful chatgpt." },
            { role: "user", content: "I need help with a conditional statement." },
            { role: "assistant", content: "Sure, what conditional statement are you working with?" },
            { role: "user", content: "Generate a set of test cases that satisfy the MC/DC coverage criterion for the following boolean expression." },
            { role: "assistant", content: "Sure, what boolean expresion are you working with?" },
            { role: "user", content: "With the following boolean expression:" + eq + "." },
            { role: "user", content: "Represent the solution as a list in Python, where each test case is a dictionary with the format {variable: value}" },
            { role: "user", content: "Respond exclusively with the Python list, no explanations, notes or extra text, just the requested pyhton list." }
        ];
        console.log("== RESPUESTA DEL CHAT==");
        const client = new OpenAIClient(endpoint, new AzureKeyCredential(azureApiKey));
        const deploymentId = "generacion-de-casos";
        const result = await client.getChatCompletions(deploymentId, messages);
        for (const choice of result.choices) {
            vscode.window.showInformationMessage(choice.message.content);
        }
    }
    catch (error) {
        console.error('Error generating test cases:', error);
        vscode.window.showErrorMessage('Failed to generate test cases. See console for details.');
    }
}
//Extension main function----------------------------------------------------------------
async function activate(context) {
    //Al iniciar extension para prepara el entorno
    const configDetails = await readConfig();
    prepareEnvironment(configDetails);
    //PYENV------------------------------------------------------------------------------
    //Comando llamada solve + argumento INPUT
    let exec_input = vscode.commands.registerCommand('testaigenerator.exec_input', async () => {
        console.log("Starting with MCDC_Framework interaction");
        //Input eq
        const eq = await vscode.window.showInputBox({
            prompt: 'Escribe la condición',
            placeHolder: 'Eq'
        });
        if (eq !== undefined) {
            vscode.window.showInformationMessage(`La eq a estudiar es: ${eq}`);
            //run_exec(context, "'"+eq+"'");
        }
        else {
            vscode.window.showErrorMessage('No se ingresó ningún parámetro.');
        }
        console.log("Done with MCDC_Framework interaction");
    });
    context.subscriptions.push(exec_input);
    //Comando llamada solve + argumento SELECCION
    let exec_select = vscode.commands.registerCommand('testaigenerator.exec_select', async () => {
        console.log("Starting with MCDC_Framework interaction");
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No hay ningún editor abierto.');
            return;
        }
        const eq = editor.document.getText(editor.selection);
        if (!eq) {
            vscode.window.showErrorMessage('No hay texto seleccionado.');
            return;
        }
        console.log("Done with MCDC_Framework interaction");
        //run_exec(context, "'"+eq+"'");
    });
    context.subscriptions.push(exec_select);
    //LLMs-------------------------------------------------------------------------------
    let llmGenerator = vscode.commands.registerCommand('executeia.EjecutarIA', () => {
        console.log('Activating executeia in azure folder...');
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No hay ningún editor abierto.');
            return;
        }
        const expresion = editor.document.getText(editor.selection);
        if (!expresion) {
            vscode.window.showErrorMessage('No hay texto seleccionado.');
            return;
        }
        console.log("Done with AI interaction");
        //generateTestCases(configDetails, expresion);
    });
    context.subscriptions.push(llmGenerator);
}
exports.activate = activate;
// This method is called when your extension is deactivated
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map