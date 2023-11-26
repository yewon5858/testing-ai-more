#!/bin/bash

# Instalar las dependencias del sistema
sudo apt-get install -y gcc make libgmp3-dev

# Instalar Requisitos
pip install -r requirements.txt

# Instalar solver MSat en pysmt 
pysmt-install --msat
