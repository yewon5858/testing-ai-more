from setuptools import setup, find_packages
#pip3 install -e .

# Leemos de requirements.txt la informacion requerida de cada paquete para usarlo 
try: 
    with open("requirements.txt","r")as file:
        required_packages=file.read().splitlines()
except FileNotFoundError:
    raise RuntimeError("No se encontró el archivo requirements.txt")
    
    
setup(
    name="TFG_testing_ai",
    version="0.1.0",
    description=" Todo lo necesario para ejecutar el codigo de este TFG_testing_ai",
    author="Gonzalo Contreras Gordo e Ismael Barahona Cánovas",
    author_email="goncontr@ucm.es y isbaraho@ucm.es",
    classifiers=["Programming Language :: Python :: 3.8"],
    packages=find_packages(),
    install_requires=required_packages,
    #duda de si probar mas versiones dado que dijimos que con la 3.10 no iba el motor 
    python_requires ='>=3.8',
      
)