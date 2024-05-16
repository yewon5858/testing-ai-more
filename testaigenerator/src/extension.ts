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
let client: any;

//Ejecutar py-MCDC + argumento
function run_exec(context: vscode.ExtensionContext, eq: string) {
    // Ejecutar el script Python en el terminal
    twsl.sendText(`python exec.py ${eq} > out.txt`); 
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
        vscode.window.showInformationMessage(`Preparando entorno, no cerrar el terminal ${twsl.name}`);
    }
    catch{
        vscode.window.showInformationMessage('Error al preparar el entorno');
    }

    try{  
        const endpoint = configDetails.endpoint;
        const azureApiKey = configDetails.apiKey;
        client = new OpenAIClient(endpoint, new AzureKeyCredential(azureApiKey));
    }
    catch(error){
        console.error('Error client:', error);
        vscode.window.showErrorMessage('Failed to create client. See console for details.');
    }
}

//LLMs-----------------------------------------------------------------------------------

//Comprobacion MC/DC
let exprLLM: string;
let intentos: number;

function comprobacion_mcdc(context: vscode.ExtensionContext, eq: string, answer: string) {
    // Ejecutar el script Python en el terminal
    twsl.sendText(`python comprob.py "${eq}" "${answer}" > comprobacion.txt`); 
}

function contenidoEntreCorchetes(texto: string): string {
    let contenido = "";
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
            contenido += contenidoActual;
            contenidoActual = ''; 
        } 
        else if (dentroCorchetes) {
            contenidoActual += caracter;
        }
    }
    return contenido;
}

let answer: string;
async function generateTestCases(context: vscode.ExtensionContext, client:any, eq: string, wrong: boolean, fallo: string) {   
    let result: any;
    const deploymentId = "generacion-de-casos";
    if(!wrong){
        try {
            const messages = [
                { role: "system", content: "You are an expert generating test cases that satisfy the MC/DC coverage criterion." },
                { role: "user", content: "I need help with test case generation, that satisfy the MC/DC coverage criterion" },
                { role: "assistant", content: "Okay, I'm an expert in that criterion. Tell me what I need to do ?" },
                { role: "user", content: "I provide you an example, in this case the boolean expression is (a<10)&(b<9)." },
                { role: "user", content: "And the output I get is in the style [{'a': 0, 'b': 0}, {'a': 11, 'b': 0}, {'a': 11, 'b': 9}]." },
                { role: "user", content: "Giving you boolean expressions, can you provide me with responses in the same style as the one I just showed you?" },        
                { role: "assistant", content: "Of course! What type of test cases are you trying to generate?" },
                { role: "user", content: "I want to generate the minimum test cases that satisfy the MC/DC coverage criterion for a boolean expression." },
                { role: "assistant", content: "Understood. Please provide the boolean expression for which you want to generate test cases." },
                { role: "user", content: "The boolean expression is as follows: "+eq+"." },
                { role: "user", content: "Respond with only the Python list, no explanations or extra text, just the requested list please." }
            ];
            console.log("== RESPUESTA DEL CHAT==");
            result = await client.getChatCompletions(deploymentId, messages);
            
        } catch (error) {
            console.error('Error generating test cases:', error);
            vscode.window.showErrorMessage('Failed to generate test cases. See console for details.');
        }
    }
    else{
        try {
            const messages2=[
                { role: "user", content: "Your response is wrong please tell me a respond that is better " },
                { role: "user", content: "la razon es " + fallo },
                { role: "user", content: "Remember that the MC/DC coverage criterion stands out for its high reliability in systems with complex decision structures and only requires n+1 test cases for decisions with n conditions."+
                "MC/DC coverage ensures that the program meets the following criteria:"+
                "Each entry and exit point of the program is executed at least once."+
                "Every condition in a program decision has been evaluated to both true and false at least once."+
                "Every decision in the program has been evaluated to both true and false at least once."+
                "Each condition in a decision independently affects the decision's evaluation." },
                { role: "user", content: "I want to generate the minimum test cases that satisfy the MC/DC coverage criterion for a boolean expression." },
                { role: "assistant", content: "Understood. Please provide the boolean expression for which you want to generate test cases." },
                { role: "user", content: "The boolean expression is as follows: "+eq+"." },
                { role: "user", content: "Respond with only the Python list following this format [{'a': 0, 'b': 0}, {'a': 11, 'b': 0}, {'a': 11, 'b': 9}], no explanations or extra text, just the requested list please." },
                { role: "assistant", content: "Sorry i give you a better solution" },
            ];
            console.log("== RESPUESTA DEL CHAT==");
            result = await client.getChatCompletions(deploymentId, messages2);
        }
        catch (error) {
            console.error('Error generating test cases:', error);
            vscode.window.showErrorMessage('Failed to generate test cases. See console for details.');
        }
    }

    // desplegable en la ventana creada 
    for (const choice of result.choices) {
        answer = contenidoEntreCorchetes(choice.message.content);

        comprobacion_mcdc(context, eq, answer);
        
    }

    // Mostrar la lista de valores de prueba en la consola
    const testCasesMessage = result.choices[result.choices.length - 1].message.content
    console.log(testCasesMessage);

}

//Extension main function----------------------------------------------------------------
export async function activate(context: vscode.ExtensionContext) {
    //Al iniciar extension para prepara el entorno
        const configDetails = await readConfig(context);
        prepareEnvironment(configDetails);

    //PYMCDC-----------------------------------------------------------------------------

    //Watcher para out.txt
    const filePathOut = context.extensionPath + '/mcdc_test/out.txt';

    const watcherOut = fs.watch(filePathOut, (event, filename) => {
        if (event === 'change') {
            fs.readFile(filePathOut, 'utf8', (err, data) => {
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
    const disposeWatcherOut = () => {
        watcherOut.close();
    };
    context.subscriptions.push({ dispose: disposeWatcherOut });

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

    //Watcher para comprobacion.txt
    const filePathCompr = context.extensionPath + '/mcdc_test/comprobacion.txt';

    const watcherCompr = fs.watch(filePathCompr, (event, filename) => {
        if (event === 'change') {
            fs.readFile(filePathCompr, 'utf8', (err, data) => {
                if (err) {
                    console.error('Error al leer el archivo:', err);
                    return;
                }
                // Muestra el contenido del archivo en un mensaje informativo
                if(data.trim() === "1" || "2" || "3"){      
                    intentos = intentos + 1;
                    //Explicacion del fallo
                    let fallo = "";
                    switch(data.trim()){
                        case "1":
                            fallo = "...";
                        break;
                        case "2":
                            fallo = "...";
                        break;
                        case "3":
                            fallo = "...";
                        break;
                    }
                    
                    //Llamada a funcion
                    vscode.window.showErrorMessage('Generando una respuesta válida...');
                    if(intentos <= 2){ // 3 intentos   
                        generateTestCases(context, client, exprLLM, false, fallo);
                    }
                    else{   
                        vscode.window.showErrorMessage('Numero de intentos excedido.');
                    }
                }
                else if(data.trim() === 'True'){
                    vscode.window.showInformationMessage(`Casos de prueba generados (LLM): `+ answer);
                }
            });
        }
    });

    // Dispose del watcher
    const disposeWatcherCompr = () => {
        watcherCompr.close();
    };
    context.subscriptions.push({ dispose: disposeWatcherCompr });
    
    let llmGenerator = vscode.commands.registerCommand('executeia.EjecutarIA', () => {
        console.log('Activating executeia in azure folder...');
        const editor = vscode.window.activeTextEditor;
        if(!editor) {
            vscode.window.showErrorMessage('No hay ningún editor abierto.');
            return;
        }

        const expresion = editor.document.getText(editor.selection);
        exprLLM = expresion;
        if(!expresion)
        {
            vscode.window.showErrorMessage('No hay texto seleccionado.');
            return;
        }
        intentos = 0;
		generateTestCases(context, client, expresion, true, "");
		
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
            exprLLM = eq;
            vscode.window.showInformationMessage(`La eq a estudiar es: ${eq}`);
            run_exec(context, "'"+eq+"'");
            intentos = 0;
            generateTestCases(context, client, eq, true, "");
        } else {
            vscode.window.showErrorMessage('No se ingresó ningún parámetro.');
        }

    });
    context.subscriptions.push(exec_input);

}

// This method is called when your extension is deactivated
export function deactivate() {}