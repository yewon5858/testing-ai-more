#!/bin/bash

# Install requirements
pip3 install -r requirements.txt

# Install system dependencies
sudo apt-get install -y gcc make libgmp3-dev

# Install pysmt
pip3 install pysmt

# Check for the installation status of pysmt
pysmt-install --check

# Install MSat solver in pysmt
pysmt-install --msat

# Display a completion message
echo "All necessary elements have been installed in your environment"