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
const path = __importStar(require("path"));
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
    twsl.sendText(`python exec.py ${eq} | tail -n 1 > out.txt`);
    //Obtener salida por mensaje informativo
    const rutaArchivo = vscode.Uri.file(path.join(context.extensionPath, '/mcdc_test/out.txt'));
    //Creacion de watcher para el fichero de salida
    const watcher = vscode.workspace.createFileSystemWatcher(rutaArchivo.fsPath);
    //Registra un cambio en el archivo
    watcher.onDidChange((event) => {
        // Leer el contenido del archivo
        vscode.workspace.fs.readFile(rutaArchivo).then(data => {
            const contenido = Buffer.from(data).toString('utf-8');
            console.log(contenido);
            vscode.window.showInformationMessage(`Casos de prueba generados (pyMCDC): ` + contenido);
        }, error => {
            console.error('Error al leer el archivo:', error);
        });
    });
    // Dispose del watcher cuando el contexto se desactive
    context.subscriptions.push(watcher);
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
        twsl.sendText(`pyenv activate ${configDetails.pyenvActivation}`);
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
function contenidoEntreCorchetes(texto) {
    const contenido = [];
    let dentroCorchetes = false;
    let contenidoActual = '';
    for (const caracter of texto) {
        if (caracter === '[') {
            dentroCorchetes = true;
            contenidoActual = '['; // Corchete de apertura
        }
        else if (caracter === ']') {
            dentroCorchetes = false;
            contenidoActual += ']'; // Corchete de cierre
            contenido.push(contenidoActual);
            contenidoActual = '';
        }
        else if (dentroCorchetes) {
            contenidoActual += caracter;
        }
    }
    return contenido;
}
async function generateTestCases(configDetails, eq) {
    try {
        const endpoint = configDetails.endpoint;
        const azureApiKey = configDetails.apiKey;
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
            { role: "user", content: "The boolean expression is as follows: " + eq + "." },
            { role: "user", content: "Respond with only the Python list, no explanations or extra text, just the requested list please." }
        ];
        console.log("== RESPUESTA DEL CHAT==");
        const client = new OpenAIClient(endpoint, new AzureKeyCredential(azureApiKey));
        const deploymentId = "generacion-de-casos";
        const result = await client.getChatCompletions(deploymentId, messages);
        // desplegable en la ventana creada 
        for (const choice of result.choices) {
            const answer = contenidoEntreCorchetes(choice.message.content);
            vscode.window.showInformationMessage(`Casos de prueba generados (LLM): ` + answer);
            /*
            twsl.show();
            twsl.sendText(`echo `+answer);
            */
        }
        // Mostrar la lista de valores de prueba en la consola
        const testCasesMessage = result.choices[result.choices.length - 1].message.content;
        console.log(testCasesMessage);
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
        //Input eq
        const eq = await vscode.window.showInputBox({
            prompt: 'Escribe la condición',
            placeHolder: 'Eq'
        });
        if (eq !== undefined) {
            vscode.window.showInformationMessage(`La eq a estudiar es: ${eq}`);
            run_exec(context, "'" + eq + "'");
        }
        else {
            vscode.window.showErrorMessage('No se ingresó ningún parámetro.');
        }
    });
    context.subscriptions.push(exec_input);
    //Comando llamada solve + argumento SELECCION
    let exec_select = vscode.commands.registerCommand('testaigenerator.exec_select', async () => {
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
        run_exec(context, "'" + eq + "'");
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
        generateTestCases(configDetails, expresion);
    });
    context.subscriptions.push(llmGenerator);
}
exports.activate = activate;
// This method is called when your extension is deactivated
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map