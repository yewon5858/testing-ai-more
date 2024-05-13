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
## Herramientas de desarrollo  
Uso de VS Code   
Uso de wsl  
Uso de Typescript  
Uso de Python 3.8  
## Dependencias de la extension
Para emplear la conexion con Azure  
+-- @azure/openai@1.0.0-beta.12   
Para el funcionamiento de la extension en visual    
Desarrollo en Typescript:   
+-- @types/mocha@10.0.6  
+-- @types/node@18.19.17  
+-- @types/vscode@1.86.0  
+-- @typescript-eslint/eslint-plugin@6.21.0  
+-- @typescript-eslint/parser@6.21.0   
`-- typescript@5.3.3  
Herramientas de prueba:  
+-- @vscode/test-cli@0.0.4  
+-- @vscode/test-electron@2.3.9  
Herramientas de analisis de codigo:  
+-- eslint@8.56.0  

## Dependencias en el entorno de wsl  
Instaladas con la creacion de un entorno con python 3.8    
|Package           |   Version|  
|-------------------|-----------|
| python             |3.8.18  |
|setuptools          |56.0.0  |
|pip                 |23.0.1  |
|more-itertools      |10.2.0  |
|pyeda               |0.29.0  |
|PySMT               |0.9.5  |
|sortedcontainers    |2.4.0  |
|TFG-testing-ai      |0.1.0|  

 ## Preparacion del entorno de wsl de manera automatica  
- [ ] Primero debemos crear nuestro entorno con python -->`pyenv virtualenv 3.8 <nombre del entorno>`
- [ ] En caso de no activares el entorno directamente emplear el comando -->`pyenv activate <nombre del entorno>`
- [ ] Debemos estar presentes en el directorio [mcdc_test_generator](/mcdc_test_generator/)     
- [ ] Segundo paso transformar nuestro install.sh con el comando -->`dos2unix install.sh`  
- [ ] Tercer paso ejecutar el archivo .sh -->`./install.sh`
- [ ] Saltara un mensaje de ¿continuar?, debemos responder que si.  
- [ ] Ya tendriamos nuestro entorno preparado para poder ser usado en la extension  
## Paso a paso de la creacion del entorno de wsl
En nuestro caso al emplear windows como sistema operativo hemos empleado la herramienta wsl para poder crear entornos virtuales con el sistema operativo Linux, pues resultaba más comodo para ejecutar el codigo de mcdc_test.  
Para el correcto funcionamiento de este entorno hemos empleado los siguientes pasos:
- [ ] Creamos un entorno virtual con python 3.8 --> `pyenv virtualenv 3.8 <nombre del entorno>`  
- [ ] En caso de no activarse el entorno directamente emplear el comando -->`pyenv activate <nombre del entorno>`
- [ ] Debemos estar presentes en el directorio [mcdc_test_generator](/mcdc_test_generator/)   
- [ ] Para instalar la libreria de tfg-testing-ai usamos el comando -->`pip install .`
- [ ] Para instalar todas las dependencias necesarias usamos el comando -->`pip install -r requirements.txt`
- [ ] Emplear los comandos siguientes para instalar las terminaciones necesarias para el Solver del codigo (Necesitamos permisos de administrador por lo tanto todo comando sera precedido por sudo ):  
     - [ ] `apt-get install gcc`  
     - [ ] `apt-get install make`  
     - [ ] `apt-get install libgmp3-dev`  
     - [ ] `pysmt-install --msat`  
     - [ ] Este ultimo es una forma de controlar si la instalacion de pysmt se ha llevado de manera correcta  `pysmt-install --check`  

## Instalación
Se debe configurar previamente el entorno virtual en wsl con cualquera de los dos metodos mencionados.   
Para que la conexion a traves de la plataforma Azure debemos instalar la libreria de cliente de Azure OpenAI, empleando el siguiente comando en nuestro cmd del proyecto
`npm install @azure/openai`  
Para la instalacion de los node_modules podemos emplear sobre el fallo de importacion de fs para instalar las librerias de tipos necesarias, o realizar la instalacion de las librerias a mano     
## Como ejecutar el proyecto
Para la ejecucion del proyecto empleamos el entorno virtual wsl.  
En este caso se ha creado un entorno preciso para asegurar su correcto desarrollo.    
Toda esta informacion esta presente en el archivo config.json en el cual tenemos estos apartados:    
- [ ] "terminalName": "TestAI_Gen", un nombre para diferenciar la terminal que se emplea para el desarrollo de nuestra expresion   
- [ ] "shellPath": "wsl", para la creacion de una terminal que use wsl       
- [ ] "pyenvActivation": "(nombre del entorno creado en wsl)", activaremos el entorno para tener todas las dependencias de la generacion por pyMCDC instaladas  
- [ ] "directoryPath": "ruta a /testaigenerator/mcdc_test",    
- [ ] "endpoint" : "https://test-ia.openai.azure.com/", el endpoint proporcionado por Azure    
- [ ] "apiKey" : "ac73454962444b47b2edb042e4033cd7"  la apikey obtenida a traves de Azure  

Empleamos F5 para abrir el modo depuracion y en este momento podemos seleccionar una expresion booleana y realizar boton derecho para seleccionar en el menu contextual cual de los dos generadores queremos emplear
o podemos hacerlo a traves de la barra de comandos  
Tras seleccionar un metodo de generacion ya directamente nos saldra la respuesta a nuestra expresion en formato lista de python con cada elemento formado por los casos de prueba  
## Ejemplo
Desde el archivo extension.ts entrar en modo depuracion usando el F5.Seleccionar una expresion booleana de enteros, emplear el boton derecho para abrir el menu contextual     
![](https://github.com/TGF-2023-24/testing-ai/assets/79473853/0d61cf5b-303e-4bb2-9d1e-fb4718c98ea9)  
Seleccionar el metodo de generacion de casos de prueba que deseamos emplear  
- [ ] Generate testcases (LLM) 
- [ ] Generate testcases (pyMCDC)   
Se nos mostrara la salida con los casos de prueba en un popup abajo a la derecha de la ventana de depuracion.    
![](https://github.com/TGF-2023-24/testing-ai/assets/79473853/9b25189e-85a8-4373-85e3-cb51ecbe17ce)  

### Licencia MIT
---



![](https://informatica.ucm.es/data/cont/media/www/pag-78821/escudofdigrande.png)
