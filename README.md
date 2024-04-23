# TFG: Generación automática de casos de prueba mediante el uso de redes neuronales/ Automatic test case generation using neural network
## Estado  
En desarrollo
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

## Dependencias de la extension
Para emplear la conexion con Azure  
+-- @azure/openai@1.0.0-beta.12   
Para el funcionamiento de la extension en visual   
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
  
|Package           |   Version|  
|-------------------|-----------|
| python             |3.8.18  |
 |gcc                 |11.4.0 |   
 |make                |4.3|
 |gmp                | 3|
 |contourpy          |1.1.1  |
|cycler             | 0.12.1 | 
|exceptiongroup     |1.2.1  |
|fonttools          | 4.51.0  |
|graphviz           | 0.20.3  |
|importlib_resources |6.4.0  |
|iniconfig           |2.0.0  |
|kiwisolver          |1.4.5  |
|matplotlib          |3.7.5  |
|more-itertools      |10.2.0  |
|numpy               |1.24.4 | 
|packaging           |24.0  |
|pandas              |2.0.3  |
|pillow              |10.3.0  |
|pip                 |23.0.1  |
|pluggy              |1.5.0  |
|pyeda               |0.29.0  |
|pyparsing           |3.1.2  |
|PySMT               |0.9.5  |
|pytest              |8.1.1  |
|python-dateutil     |2.9.0.post0|  
|pytz                |2024.1  |
|setuptools          |56.0.0  |
|six                 |1.16.0  |
|sortedcontainers    |2.4.0  |
|tomli               |2.0.1  |
|tzdata              |2024.1 | 
|zipp                |3.18.1|  
 
## Paso a paso de la creacion del entorno de wsl
En nuestro caso al emplear windows como sintema operativo hemos empleado la herramienta wsl para poder crear entornos virtuales con el sistema operativo Linux pues resultaba mas comodo para ejecutar el codigo de mcdc_test.  
Para el correcto funcionamiento de este entorno hemos empleado los siguientes pasos:
- [ ] Creamos un entorno virtual con python 3.8 --> `pyenv virtualenv 3.8 <nombre del entorno>`  
- [ ] En caso de no activares el entorno directamente emplear el comando -->`pyenv activate <nombre del entorno>`  
- [ ] Para instalar todas las dependencias necesarias usamos el comando -->`pip install -r requirements.txt`
- [ ] Dado que no se encuentra en el requirements.txt debemos instalar a mano Pysmt -->  `pip install pysmt`
- [ ] Emplear los comandos siguientes (Necesitamos permisos de administrador por lo tanto todo comando sera precedido por sudo ):  
     - [ ]    `apt-get install gcc`  
     - [ ]     `apt-get install make`  
     - [ ]  `apt-get install libgmp3-dev`  
     - [ ]   `pysmt-install --msat`  
     - [ ]    `pysmt-install --check`  

## Herramientas de desarrollo  
Uso de VS Code   
Uso de wsl  
Uso de Typescript  
Uso de Python 3.8  
## Instalación
Se debe emplear el ejecutable de nombre install.sh para obtener todos los requisitos necesarios para poder ejecutar de una manera correcta este proyecto en su dispositivo  
Para que la conexion a traves de la plataforma Azure debemos instalar la libreria de cliente de Azure OpenAI, empleando el siguiente comando en nuestro cmd del proyecto
`npm install @azure/openai`  
Ademas de emplear boton derecho sobre el fallo de importacion de fs para instalar las librerias de tipos necesarias  
## Como ejecutar el proyecto
Para la ejecucion del proyecto empleamos el entorno virtual wsl.  
En este caso se ha creado un entorno preciso para asegurar su correcto desarrollo.    
Toda esta informacion esta presente en el archivo config.json en el cual tenemos estos apartados:    
- [ ] "terminalName": "TestAI_Gen", un nombre para diferenciar la terminal que se emplea para el desarrollo de nuestra expresion   
- [ ] "shellPath": "wsl",  se refleja el uso de wsl   
- [ ] "pyenvActivation": "(nombre del entorno creado en wsl)",   activamos el entorno para tener todas las dependencias instaladas  
- [ ] "directoryPath": "ruta a /testaigenerator/mcdc_test",    
- [ ] "endpoint" : "https://test-ia.openai.azure.com/", el endpoint proporcionado por Azure    
- [ ] "apiKey" : "ac73454962444b47b2edb042e4033cd7"  la apikey obtenida a traves de Azure  
En este caso al seleccionar la opcion de generar por libreria ejecutamos el comando.  
`python exec.py 'expresion'`
Todo esto se puede ver representado al comentar la linea 67 de extension.ts, pues esta realiza un clear de la consola para mejorar asi la estetica     
En caso de seleccionar la opcion de generar por LLM
## Ejemplo
Desde el archivo extension.ts entrar en modo depuracion usando el F5.Seleccionar una expresion booleana de enteros, emplear el boton derecho para abrir el menu contextual     
![](https://github.com/TGF-2023-24/testing-ai/assets/79473853/0d61cf5b-303e-4bb2-9d1e-fb4718c98ea9)  
Seleccionar el metodo de generacion de casos de prueba que deseamos emplear  
- [ ] Generate testcases (LLM) 
- [ ] Generate testcases (pyMCDC)   
Se nos mostrara la salida con los casos de prueba en un popup abajo a la derecha de la ventana de depuracion.  

### Licencia MIT
---



![](https://informatica.ucm.es/data/cont/media/www/pag-78821/escudofdigrande.png)
