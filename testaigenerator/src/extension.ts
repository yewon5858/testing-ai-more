// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as fs from 'fs';

const { OpenAIClient, AzureKeyCredential } = require("@azure/openai");

//Interfaz de Configuración entorno pyenv:
interface Configuration {
    terminalName: string;
    shellPath: string;
    pyenvActivation: string;
    directoryPath: string;
    endpoint : string;
    apiKey : string
}

async function readConfig(): Promise<Configuration>{
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
        const configDetails: Configuration = JSON.parse(data);
        return configDetails;
    } catch (error) {
        vscode.window.showErrorMessage('Error al leer o parsear el archivo de configuración.');
        throw new Error('Error al leer o parsear el archivo de configuración.');
    }
}

//PYENV------------------------------------------------------------------------------

let twsl: vscode.Terminal;

//Ejecutar py-MCDC + parametro
function run_exec(context: vscode.ExtensionContext, eq: string) {
    // Ejecutar el script Python en el terminal
    twsl.sendText(`python exec.py ` + eq);
}

//Prepare terminal and environment
function prepareEnvironment(configDetails: Configuration){
    try{
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
    catch{
        vscode.window.showInformationMessage('Error al preparar el entorno');

    }
}

//LLMs-----------------------------------------------------------------------------------

async function generateTestCases(configDetails:Configuration, eq: string) {
        try {
            const endpoint = process.env[configDetails.endpoint];
            const azureApiKey = process.env[configDetails.apiKey];

            const messages = [
                { role: "system", content: "You are a helpful chatgpt." },
                { role: "user", content: "I need help with a conditional statement." },
                { role: "assistant", content: "Sure, what conditional statement are you working with?" },
                { role: "user", content: "Generate a set of test cases that satisfy the MC/DC coverage criterion for the following boolean expression." },
                { role: "assistant", content: "Sure, what boolean expresion are you working with?" },
                { role: "user", content: "With the following boolean expression:"+eq+"." },
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
            console.error('Error generating test cases:', error);
            vscode.window.showErrorMessage('Failed to generate test cases. See console for details.');
        }

}

//Extension main function----------------------------------------------------------------
export async function activate(context: vscode.ExtensionContext) {
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
            run_exec(context, "'"+eq+"'");
        } else {
            vscode.window.showErrorMessage('No se ingresó ningún parámetro.');
        }

    });
    context.subscriptions.push(exec_input);

    //Comando llamada solve + argumento SELECCION
    let exec_select = vscode.commands.registerCommand('testaigenerator.exec_select', async () => {

        const editor = vscode.window.activeTextEditor;
        if(!editor) {
            vscode.window.showErrorMessage('No hay ningún editor abierto.');
            return;
        }

        const eq = editor.document.getText(editor.selection);
        if(!eq){
            vscode.window.showErrorMessage('No hay texto seleccionado.');
            return;
        }

        run_exec(context, "'"+eq+"'");

    });
    context.subscriptions.push(exec_select);

    //LLMs-------------------------------------------------------------------------------

    let llmGenerator = vscode.commands.registerCommand('executeia.EjecutarIA', () => {
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
		generateTestCases(configDetails, expresion);
		
    });
	context.subscriptions.push(llmGenerator);

}

// This method is called when your extension is deactivated
export function deactivate() {}