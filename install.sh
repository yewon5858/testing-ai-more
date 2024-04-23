#!/bin/bash

# Instalar las dependencias del sistema
sudo apt-get install -y gcc make  libgmp3-dev

# Instalar Requisitos // mirar si funciona con .
pip install -r requirements.txt
# Instalar solver MSat en pysmt 
pysmt-install --msat
pysmt-install --check
 #Mostramos un mensaje de finalizacion
 echo "Todos los elementos necesarios han sido instalados en su entorno"
