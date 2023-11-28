#!/bin/bash

# Debemos de instalar nosotros python 3.8¿ pero ademas debemos tener en cuenta los diversos sistemas ?
# Verificamos si Python 3.8 está instalado
if command -v python3.8 &> /dev/null; then
    echo "Python 3.8 ya está instalado."
else
    echo "Instalando Python 3.8..."
    # Aquí se muestra un ejemplo para sistemas basados en Debian (como Ubuntu)
    sudo apt-get update
    sudo apt-get install -y python3.8
fi

# Instalar las dependencias del sistema (gcc,make y lib)
sudo apt-get install -y gcc make libgmp3-dev

# Instalar Requisitos
pip install -r requirements.txt

# Instalar solver MSat en pysmt 
pysmt-install --msat
 #Mostramos un mensaje de finalizacion
 echo "Todos los elementos necesarios han sido instalados en su entorno"
