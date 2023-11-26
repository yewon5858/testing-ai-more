import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';

import { Widget } from '@lumino/widgets';



interface APODResponse {
  copyright: string;
  date: string;
  explanation: string;
  media_type: 'video' | 'image';
  title: string;
  url: string;
};

function format_testcases(testcases:string){
  let first_open = true;
  let out = "";
  let tabs = 0;
  for(var i = 0; i<testcases.length; i++){
    if(testcases[i]=="{"){
      if(!first_open){
        tabs++;

        out+="\n";
        for(let j=0; j<tabs; j++) out += "\t";
        out += "{";
      }else{
        first_open = false;
      }
    }
    else if(testcases[i]=="}"){
      tabs--;
      for(let j=0; j<tabs; j++) out += "\t";
      if(i+1<testcases.length && testcases[i+1]==","){
        out += "},\n";
        i++;
      }
      else if(i+1<testcases.length && testcases[i+1]=="]"){
        out += "}\n]";
        i++;
      }
    }
    else if (testcases[i]=="," && testcases[i-1]==")"){
      out+=",\n";
    }
    else if (testcases[i]==":"){
      out += " =";
    }
    else if (testcases[i]=="\""){
      continue;
    }
    else{
      out+=testcases[i];
    }
  }

  return out;
}

async function foo(input:HTMLTextAreaElement, input2:HTMLInputElement, input3:HTMLInputElement, textbox:HTMLTextAreaElement){
  const url_json = 'http://127.0.0.1:5000/json';
  const url_pairs = 'http://127.0.0.1:5000/json_pairs';
  
  var logicExp = input.value;
  var maxRounds = input2.value;
  var rngRounds = input3.value;


  const data = { expression : logicExp, maxRounds: maxRounds, rngRounds: rngRounds };
  const xhr = new XMLHttpRequest();
  xhr.open('POST', url_json, true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.setRequestHeader('Access-Control', 'Allow-Origin');
  
  console.log("test foo");

  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      console.log(xhr.responseText);
    } else if (xhr.readyState === 4 && xhr.status !== 200) {
      console.error(xhr.responseText);
    }

    var testcases = xhr.responseText;

    textbox.textContent = format_testcases(testcases);
    
  };
  
  const xhr2 = new XMLHttpRequest();
  xhr2.open('POST', url_pairs, true);
  xhr2.setRequestHeader('Content-Type', 'application/json');
  xhr2.setRequestHeader('Access-Control', 'Allow-Origin');
  
  xhr2.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      console.log(xhr.responseText);
    } else if (xhr.readyState === 4 && xhr.status !== 200) {
      console.error(xhr.responseText);
    }

    var testcases = xhr.responseText;

    textbox.textContent += format_testcases(testcases);
    
  };
  

  xhr.send(JSON.stringify(data));
  //xhr2.send(JSON.stringify(data));

  console.log("text content: ", input.value)
  
}

/**
 * Initialization data for the jupyterlab_apod extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-apod',
  autoStart: true,
  requires: [ICommandPalette],
  activate: async (app: JupyterFrontEnd, palette: ICommandPalette) => {
    console.log('JupyterLab extension jupyterlab_apod is activated!');

    // Define a widget creator function,
    // then call it to make a new widget
    const newWidget = async () => {
      // Create a blank content widget inside of a MainAreaWidget
      const content = new Widget();
      const widget = new MainAreaWidget({ content });
      widget.id = 'apod-jupyterlab';
      widget.title.label = 'Astronomy Picture';
      widget.title.closable = true;

      // Add an image element to the content
      let img = document.createElement('img');
      //content.node.appendChild(img);

      // Get a random date string in YYYY-MM-DD format
      function randomDate() {
        const start = new Date(2010, 1, 1);
        const end = new Date();
        const randomDate = new Date(start.getTime() + Math.random()*(end.getTime() - start.getTime()));
        return randomDate.toISOString().slice(0, 10);
      }

      // Fetch info about a random picture
      console.log("Trying to get random image for the widget...")
      const response = await fetch(`https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&date=${randomDate()}`);
      const data = await response.json() as APODResponse;

      if (data.media_type === 'image') {
        // Populate the image
        img.src = data.url;
        img.title = data.title;
      } else {
        console.log('Random APOD was not a picture.');
      }

      console.log("Creating widget form...")
      let mydiv = document.createElement('div')

      mydiv.innerHTML = `<h2>Insert logical expression below</h2>
       `

        let input : HTMLTextAreaElement = <HTMLTextAreaElement>document.createElement("textarea")
        input.id = "logic-expression"

        let input2 : HTMLInputElement = <HTMLInputElement>document.createElement("input")
        input2.id = "maxRounds"

        let input3 : HTMLInputElement = <HTMLInputElement>document.createElement("input")
        input3.id = "rngRounds"

        let textbox : HTMLTextAreaElement = <HTMLTextAreaElement>document.createElement("textarea")

        let btn:HTMLButtonElement=<HTMLButtonElement>document.createElement("button");
        btn.appendChild(document.createTextNode("Click Me!"))

        btn.addEventListener('click', (e:Event) => foo(input, input2, input3, textbox));
        
        content.node.appendChild(mydiv)
        content.node.appendChild(input)
        content.node.appendChild(input2)
        content.node.appendChild(input3)
        content.node.appendChild(btn)
        content.node.appendChild(textbox)
      
      return widget;
    }
    
    let widget = await newWidget();
    
    // Add an application command
    const command: string = 'apod:open';
    app.commands.addCommand(command, {
      label: 'CustomCommand',
      execute: async () => {
        console.log("Trying to open widget...")

        if(widget.isAttached){
          console.log("Removing previous widget...")
          widget.dispose()   
        }

        // Regenerate the widget if disposed
        if (widget.isDisposed) {
          widget = await newWidget();
        }
        console.log(widget.isDisposed, widget.isAttached)
        if (!widget.isAttached) {
          // Attach the widget to the main work area if it's not there
          app.shell.add(widget, 'main');
        }
        
        // Activate the widget
        app.shell.activateById(widget.id);
      }
    });
    
    app.contextMenu.addItem({
      command: command,
      selector: '*'
    })

    console.log('command: '+command)

    // Add the command to the palette.
    palette.addItem({ command, category: 'Tutorial' });
  }
};

export default plugin;