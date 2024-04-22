# TFG: Generación automática de casos de prueba mediante el uso de redes neuronales/ Automatic test case generation using neural network

## Autores
Este proyecto esta realizado por **Gonzalo Contreras Gordo** e **Ismael Barahona Cánovas**
## Resumen
Todo gira entorno a la generacion de casos de prueba que cumplan el criterio MC/DC, para esto se emplean dos generadores uno utiliza el codigo de la libreria mcdc_test y otro que usa la conexion  con  un LLM a traves de la plataforma de Microsoft, Azure
## Marco teorico
El criterio **MC/DC** siendo un criterio de cobertura que destaca por su alta fiabilidad en sistemas con una compleja estructura de decisiones y que requiere únicamente n+1 casos de prueba para decisiones con n condiciones. La cobertura MC/DC garantiza que el programa cumple los siguientes criterios:  
->Cada punto de entrada y salida del programa se ejecuta al menos una vez.  
->Toda condición en una decisión del programa ha tomado todas sus posibles evaluaciones al menos una vez.  
->Cada decisión del programa ha tomado todas sus posibles evaluaciones al menos una vez.  
->Cada condición en una decisión afecta de manera independiente en la evaluación de la decisión.  

## Dependencias
+-- @azure/openai@1.0.0-beta.12  
+-- @types/mocha@10.0.6  
+-- @types/node@18.19.17  
+-- @types/vscode@1.86.0  
+-- @typescript-eslint/eslint-plugin@6.21.0  
+-- @typescript-eslint/parser@6.21.0  
+-- @vscode/test-cli@0.0.4  
+-- @vscode/test-electron@2.3.9  
+-- eslint@8.56.0  
`-- typescript@5.3.3
## Dependencias en el entorno de wsl   
## Entorno de desarrollo  
Uso de VS Code 
Uso de wsl
Uso de Typescript
Uso de Python  
## Instalación
Se debe emplear el ejecutable de nombre install.sh para obtener todos los requisitos necesarios para poder ejecutar de una manera correcta este proyecto en su dispositivo  
Para que la conexion a traves de la plataforma Azure debemos instalar la libreria de cliente de Azure OpenAI
npm install @azure/openai

## Como ejecutar el proyecto
Para la ejecucion del proyecto empleamos el entorno virtual wsl.  
En este caso se ha creado un entorno preciso para asegurar su correcto desarrollo.  
Usando pyenv activate tfg, se activa el entorno creado en wsl  
Cambiamos al directorio donde tenemos localizado nuestro codigo cd "/mnt/c/Users/Usuario01/Desktop/Universidad/CUARTO-QUINTO AÑO/TFG/testing-ai-tfm/testing-ai-tfm/testaigenerator/mcdc_test"  
Toda esta informacion esta extraida del archivo config.json en el cual tenemos estos apartados:    
- [ ] "terminalName": "TestAI_Gen", un nombre para diferenciar la terminal que se emplea para el desarrollo de nuestra expresion   
- [ ] "shellPath": "wsl",  se refleja el uso de wsl   
- [ ] "pyenvActivation": "pyenv activate (nombre del entorno creado en wsl)",   activamos el entorno para tener todas las dependencias instaladas  
- [ ] "directoryPath": "ruta a /testaigenerator/mcdc_test",    
- [ ] "endpoint" : "https://test-ia.openai.azure.com/", el endpoint proporcionado por Azure    
- [ ] "apiKey" : "ac73454962444b47b2edb042e4033cd7"  la apikey obtenida a traves de Azure   
    
En este caso al seleccionar la opcion de generar por libreria ejecutamos el comando.
python exec.py 'expresion'  
En caso de seleccionar la opcion de generar por LLM

## Estado  
En desarrollo
## Ejemplo  
### Licencia MIT
---



![](https://informatica.ucm.es/data/cont/media/www/pag-78821/escudofdigrande.png)
