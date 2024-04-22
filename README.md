# TFG: Generación automática de casos de prueba mediante el uso de redes neuronales/ Automatic test case generation using neural network

## Autores
Este proyecto esta realizado por **Gonzalo Contreras Gordo** e **Ismael Barahona Cánovas**
## Resumen
Todo gira entorno a la generacion de casos de prueba que cumplan el criterio MC/DC, para esto se emplean dos generadores uno utiliza el codigo de la libreria mcdc_test y otro que usa la conexion  con  un LLM a traves de la plataforma de Microsoft, Azure
## Marco teorico
El criterio MC/DC siendo un criterio de cobertura que destaca por su alta fiabilidad en sistemas con una compleja estructura de decisiones y que requiere únicamente n+1 casos de prueba para decisiones con n condiciones. La cobertura MC/DC garantiza que el programa cumple los siguientes criterios:  
->Cada punto de entrada y salida del programa se ejecuta al menos una vez.  
->Toda condición en una decisión del programa ha tomado todas sus posibles evaluaciones al menos una vez.  
->Cada decisión del programa ha tomado todas sus posibles evaluaciones al menos una vez.  
->Cada condición en una decisión afecta de manera independiente en la evaluación de la decisión.  


## Dependencias
+-- @azure-rest/core-client@1.2.0     
+-- @azure/abort-controller@2.0.0  
+-- @azure/core-auth@1.6.0  
+-- @azure/core-rest-pipeline@1.14.0  
+-- @azure/core-sse@2.0.0  
+-- @azure/core-tracing@1.0.1  
+-- @azure/core-util@1.7.0  
+-- @azure/logger@1.0.4  
+-- @azure/openai@1.0.0-beta.11  
+-- @tootallnate copy/once@npm:@tootallnate/once@2.0.0  
+-- @types copy/node@npm:@types/node@20.11.25  
+-- @types/mocha@10.0.6  
+-- @types/node@18.19.17  
+-- @types/vscode@1.86.0  
+-- @typescript-eslint/eslint-plugin@6.21.0  
+-- @typescript-eslint/parser@6.21.0  
+-- @vscode/test-cli@0.0.4  
+-- @vscode/test-electron@2.3.9  
+-- agent-base copy@npm:agent-base@6.0.2  
+-- chalk copy@npm:chalk@5.3.0  
+-- debug copy@npm:debug@4.3.4  
+-- dotenv@16.4.5  
+-- eslint@8.56.0  
+-- http-proxy-agent copy@npm:http-proxy-agent@5.0.0  
+-- https-proxy-agent copy@npm:https-proxy-agent@5.0.1  
+-- ms copy@npm:ms@2.1.2  
+-- tslib@2.6.2  
+-- typescript@5.3.3
`-- undici-types copy@npm:undici-types@5.26.5  
## Instalación
Se debe emplear el ejecutable de nombre install.sh para obtener todos los requisitos necesarios para poder ejecutar de una manera correcta este proyecto en su dispositivo


## Como ejecutar el proyecto

##  Extension 
Empleada una conexion a Azure Microsoft
## Estado  
En desarrollo
## Ejemplo  
### Licencia MIT
---



![](https://informatica.ucm.es/data/cont/media/www/pag-78821/escudofdigrande.png)
