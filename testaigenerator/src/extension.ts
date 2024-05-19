// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

//  Import the specific classes from @azure/openai package 
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
//variable global para poder ser usada en el renvio en caso de fallo 
let answer: string;
async function generateTestCases(context: vscode.ExtensionContext, client:any, eq: string, wrong: boolean, fail: string) {   
    let result: any;
    const deploymentId = "generacion-de-casos";
    const messages = [
        { role: "system", content: "You're an expert at generating test cases that satisfy the MC/DC coverage criterion.." },
        { role: "user", content: "I need help generating test cases that satisfy the MC/DC coverage criterion." },
        { role: "user", content: "The MC/DC coverage criterion stands out for its high reliability in systems with complex decision structures and only requires n+1 test cases for decisions with n conditions."+
             "MC/DC coverage ensures that the program meets the following criteria:"+
            "Each entry and exit point of the program is executed at least once."+
            "Every condition in a program decision has been evaluated to both true and false at least once."+
            "Every decision in the program has been evaluated to both true and false at least once."+
            "Each condition in a decision independently affects the decision's evaluation." },
        { role: "assistant", content: "Sure thing! I'm an expert in that. What do you need help with?" },
        { role: "user", content: "I'll give you an example. Let's say the boolean expression is (a<10)&(b<9)." },
        { role: "user", content: "The output I get follows this format [{'a': 0, 'b': 0}, {'a': 11, 'b': 0}, {'a': 11, 'b': 9}]"+
         "Each element of the list is a dictionary containing key-value pairs. In this case, the keys are 'a' and 'b', and their corresponding values are integers."+
        "Here's the detailed explanation of the list:"+
        "{'a': 0, 'b': 0}: This is the first dictionary in the list. It represents a set of values where the value of 'a' is 0 and the value of 'b' is also 0. "+
        "{'a': 11, 'b': 0}: This is the second dictionary in the list. Here, the value of 'a' is 11 and the value of 'b' is 0."+
        "{'a': 11, 'b': 9}: This is the third dictionary in the list. In this case, the value of 'a' is 11 and the value of 'b' is 9."+
       "In summary, the provided list contains three sets of values represented as dictionaries, where each dictionary has keys 'a' and 'b' with specific values associated with them" },
        { role: "user", content: "Can you provide responses in the same style for other boolean expressions?" },        
        { role: "assistant", content:"Absolutely! What specific test cases are you looking to generate?" },
        { role: "user", content: "I want to generate the minimum test cases that satisfy the MC/DC coverage criterion for a boolean expression." },
        { role: "assistant", content: "Got it. Could you please provide the boolean expression you're working with?" },
        { role: "user", content: "The boolean expression is : "+eq+"." },
        { role: "user", content: "Please provide the list in Python format without additional explanations." },
        { role: "assistant", content: "Understood, the expression you provided is:"+eq+". Is it correct?" },
        { role: "user", content: "Yes it is" },
    ];
    //si es una respuesta correcta 
    if(!wrong){
        try {
            console.log("== RESPUESTA DEL CHAT==");
            result = await client.getChatCompletions(deploymentId, messages);
            
        } catch (error) {
            console.error('Error generating test cases:', error);
            vscode.window.showErrorMessage('Failed to generate test cases. See console for details.');
        }
    }
    // si es una respuesta erronea
    else{
        
        try {
            // creamos dos mensajes nuevos con la respuesta erronea y el motivo del fallo 
            const extra=[
                { role: "user", content: "Your previous response \"" + answer + "\" appears to be incorrect. The reason for the error may be due to: " + fail + ". Please review your response and make the necessary corrections." },
                { role: "user", content: "Make sure to follow the correct format and logic when providing your response." }
            ];
            // juntamos los mensajes anteriores con los nuevos para volver a pedir solucion
            const messages2=[...messages,...extra ];
            //para visionar todo el conjunto de mensajes
            console.log("== MENSAJE AL CHAT CUANDO ESTA MAL ==");
            console.log(messages2);
            // nueva respuesta 
            result = await client.getChatCompletions(deploymentId, messages2);
        }
        catch (error) {
            console.error('Error generating test cases:', error);
            vscode.window.showErrorMessage('Failed to generate test cases. See console for details.');
        }
    }

    // desplegable en la ventana creada 
    for (const choice of result.choices) {
        // nos quedamos solo con la lista de los casos de prueba
        answer = contenidoEntreCorchetes(choice.message.content);
        // comprobamos si la solucion cumnple los criterios que queremos entorno a MCDC
        comprobacion_mcdc(context, eq, answer);
    }

    // Mostrar la respuesta completa del chat por consola por si quiere visionarse de manera mas amplia
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
                if(data.trim() !== "")
                {
                    // Muestra el contenido del archivo en un mensaje informativo
                    vscode.window.showInformationMessage(`Casos de prueba generados (pyMCDC): ${data}`);
                }
               
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
                 if(data.trim() === "1" ||data.trim() ===  "2" ||data.trim() ===  "3"){      
                    intentos = intentos + 1;
                    //Explicacion del fallo
                    let fail = "";
                    switch(data.trim()){
                        case "1":
                            fail = "Failure because the number of test cases generated exceeds the maximum allowed (2n) or does not reach the minimum (n+1)";
                            break;
                        case "2":
                            fail = "Failure because some variable does not have a test case for both true and false ";
                            break;
                        case "3":
                            fail = "Failure because the number of test cases generated exceeds the maximum allowed (2n) or does not reach the minimum (n+1) and because some variable does not have a test case for both true and false ";
                            break;
                    }
                    
                    //Llamada a funcion
                    vscode.window.showErrorMessage('Generando una respuesta válida...');
                    if(intentos <= 2){ // 3 intentos   
                        generateTestCases(context, client, exprLLM, true, fail);
                    }
                    else{   
                        vscode.window.showErrorMessage('Numero de intentos excedido.');
                    }
                }
                 if(data.trim() === "True"){
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
		generateTestCases(context, client, expresion, false, "");
		
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