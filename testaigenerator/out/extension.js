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
let twsl;
// Función para ejecutar setta
function run_setta(context) {
    // Ejecutar el script Python en el terminal
    twsl.sendText(`python example.py`);
}
//Función ejecutar + parametro
function run_exec(context, eq) {
    // Ejecutar el script Python en el terminal
    twsl.sendText(`python exec.py ` + eq);
}
//FUNCION PARA PREPARAR EL ENTORNO EN LA TERMINAL
function preparePyenv() {
    //Crear terminal wsl
    twsl = vscode.window.createTerminal({
        name: 'TestAI_Gen', // Puedes cambiar el nombre si lo deseas
        shellPath: 'wsl', // Especifica el ejecutable de WSL
        shellArgs: [], // Argumentos adicionales para el shell de WSL si es necesario
    });
    twsl.show();
    //Comandos de preparacion
    twsl.sendText('pyenv activate TFG');
    twsl.sendText('cd /mnt/c/TFG/testaigenerator/mcdc_test');
    twsl.sendText('clear');
    if (twsl) {
        // La terminal está abierta
        vscode.window.showInformationMessage('Entorno preparado, no cerrar el terminal TestAI_Gen');
    }
    else {
        vscode.window.showInformationMessage('Error al preparar el entorno');
    }
}
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
function activate(context) {
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
            run_exec(context, "'" + eq + "'");
        }
        else {
            vscode.window.showErrorMessage('No se ingresó ningún parámetro.');
        }
    });
    context.subscriptions.push(exec_input);
    //Comando llamada solve + argumento texto seleccionado
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
}
exports.activate = activate;
// This method is called when your extension is deactivated
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map