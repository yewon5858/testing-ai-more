// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

let twsl: vscode.Terminal;

//Interfaz de Configuración:
interface Configuration {
    terminalName: string;
    shellPath: string;
    pyenvActivation: string;
    directoryPath: string;
}

// Función para ejecutar setta
function run_setta(context: vscode.ExtensionContext) {
    // Ejecutar el script Python en el terminal
    twsl.sendText(`python example.py`);
}

//Función ejecutar + parametro
function run_exec(context: vscode.ExtensionContext, eq: string) {
    // Ejecutar el script Python en el terminal
    twsl.sendText(`python exec.py ` + eq);
}

//FUNCION PARA PREPARAR EL ENTORNO Y LA TERMINAL
function preparePyenv(){

    //Path to config.json
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('No se encontraron carpetas en el espacio de trabajo.');
        return;
    }
    const workspaceFolder = workspaceFolders[0];
    const parentFolder = vscode.Uri.joinPath(workspaceFolder.uri, '../'); //Directorio padre
    const configFilePath = vscode.Uri.joinPath(parentFolder, 'config.json');

    //Read config.json
    console.log(configFilePath); // Agregar esta línea para verificar la ruta
    fs.readFile(configFilePath.fsPath, 'utf8', (err,data) => {
        if(err){
            vscode.window.showErrorMessage('Error al leer el archivo de configuración.');
            return;
        }

        try{
            const config: Configuration = JSON.parse(data);

            //Crear terminal wsl
            twsl = vscode.window.createTerminal({
                name: config.terminalName, // Puedes cambiar el nombre si lo deseas
                shellPath: config.shellPath, // Especifica el ejecutable de WSL
                shellArgs: [], // Argumentos adicionales para el shell de WSL si es necesario
            });
            twsl.show();
            //Comandos de preparacion
            twsl.sendText(config.pyenvActivation);
            twsl.sendText(`cd ${config.directoryPath}`);
            twsl.sendText('clear');

            // La terminal está abierta
            vscode.window.showInformationMessage(`Entorno preparado, no cerrar el terminal ${twsl.name}`);
        }
        catch{
            vscode.window.showInformationMessage('Error al preparar el entorno');

        }
    });
}

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

    //Al iniciar extension para prepara el entorno
    preparePyenv();

	let disposable = vscode.commands.registerCommand('testaigenerator.helloWorld', () => {
		// The code you place here will be executed every time your command is executed
		// Display a message box to the user
		vscode.window.showInformationMessage('Hello World from TestAIGenerator!');
	});
	context.subscriptions.push(disposable);
    
	//Comando ejecutar programa python
	let settaexec = vscode.commands.registerCommand('testaigenerator.settaexec', () => {
        run_setta(context);
    });
    context.subscriptions.push(settaexec);

    //Comando llamada solve + argumento escrito por input
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

    //Comando llamada solve + argumento texto seleccionado
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

}

// This method is called when your extension is deactivated
export function deactivate() {}
