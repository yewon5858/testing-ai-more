// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

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

async function readConfig(context: vscode.ExtensionContext): Promise<Configuration>{
    const configFilePath = path.join(context.extensionPath, 'config.json');
    try {
        const data = await fs.promises.readFile(configFilePath, 'utf8');
        const configDetails: Configuration = JSON.parse(data);
        return configDetails;
    } catch (error) {
        console.error('Error al leer o parsear el archivo de configuración:', error);
        throw new Error('Error reading or parsing config file');
    }
}

//PYENV------------------------------------------------------------------------------

let twsl: vscode.Terminal;

//Ejecutar py-MCDC + argumento
function run_exec(context: vscode.ExtensionContext, eq: string) {
    // Ejecutar el script Python en el terminal
    twsl.sendText(`python exec.py ${eq} > out.txt`);
    
    const filePath = context.extensionPath + '/mcdc_test/out.txt';

    // Crea un Watcher para el archivo de salida
    const watcher = fs.watch(filePath, (event, filename) => {
        if (event === 'change') {
            fs.readFile(filePath, 'utf8', (err, data) => {
                if (err) {
                    console.error('Error al leer el archivo:', err);
                    return;
                }
                // Muestra el contenido del archivo en un mensaje informativo
                vscode.window.showInformationMessage(`Casos de prueba generados (pyMCDC): ${data}`);
            });
        }
    });

    // Dispose del watcher
    const disposeWatcher = () => {
        watcher.close();
    };
    context.subscriptions.push({ dispose: disposeWatcher }); 
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
        twsl.sendText(`pyenv activate ${configDetails.pyenvActivation}`);
        twsl.sendText(`cd "${configDetails.directoryPath}"`);
        twsl.sendText('clear');

        //Environment ready to use
        vscode.window.showInformationMessage(`Entorno preparado, no cerrar el terminal ${twsl.name}`);
    }
    catch{
        vscode.window.showInformationMessage('Error al preparar el entorno');

    }
}

//LLMs-----------------------------------------------------------------------------------
function contenidoEntreCorchetes(texto: string): string[] {
    const contenido: string[] = [];
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

async function generateTestCases(configDetails:Configuration, eq: string) {   
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
            { role: "user", content: "The boolean expression is as follows: "+eq+"." },
            { role: "user", content: "Respond with only the Python list, no explanations or extra text, just the requested list please." }
        ];
        console.log("== RESPUESTA DEL CHAT==");
        const client = new OpenAIClient(endpoint, new AzureKeyCredential(azureApiKey));
        const deploymentId = "generacion-de-casos";
        const result = await client.getChatCompletions(deploymentId, messages);
        // desplegable en la ventana creada 
        for (const choice of result.choices) {
            const answer = contenidoEntreCorchetes(choice.message.content);
            vscode.window.showInformationMessage(`Casos de prueba generados (LLM): `+ answer);
        }

        // Mostrar la lista de valores de prueba en la consola
        const testCasesMessage = result.choices[result.choices.length - 1].message.content
        console.log(testCasesMessage);
    } catch (error) {
        console.error('Error generating test cases:', error);
        vscode.window.showErrorMessage('Failed to generate test cases. See console for details.');
    }

}

//Extension main function----------------------------------------------------------------
export async function activate(context: vscode.ExtensionContext) {
    //Al iniciar extension para prepara el entorno
        const configDetails = await readConfig(context);
        prepareEnvironment(configDetails);

    //PYMCDC-----------------------------------------------------------------------------

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

    //BOTH LLM & pyMCDC
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
            generateTestCases(configDetails, eq);
        } else {
            vscode.window.showErrorMessage('No se ingresó ningún parámetro.');
        }

    });
    context.subscriptions.push(exec_input);

}

// This method is called when your extension is deactivated
export function deactivate() {}