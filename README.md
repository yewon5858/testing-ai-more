# Large Language Modul integration VSCode Plugin (SmartMCDC-VS-Plugin)

This repository is a monorepo containing the following components:

  - **py-mcdc**: Developed by Faustin Ahishakiye, José Ignacio Requeno Jarabo, Kars Michael Kristensen, and Volker Stolz. This component is located in the folder mcdc_test. Link to the original Repo.
  - **API-Endpoint**: A Flask RESTful web service providing access to the test generation functionality of py-mcdc.
  - **testaigenerator**: An implementation of the interface integrating Language Models (LLMs) and py-mcdc into VSCode.
  - **Azure**: A prototype for connecting and interacting with AzureGPT.
  - **ChatGPT**: A prototype for connecting and interacting with ChatGPT.

# testaigenerator

----
Installation of vscode plugin

- Set it up in a Linux based OS
- Install nvs (if multiple node versions are requiered)
- Install node 
- Install a npm version >= 16
- Then execute npm install (or ci)
(- Then tsc on the extension file)
- Sometime the command: npm run compile has to be executed before the plugin can be started
- Just open the project folder (of aitestgeneration) and then press F5
- Change the configer file to the needs of the user 
(I have to configer that the docker will be called) 
- before running the plugin be sure to run the docker file 


--> I have to reinstall the node and npm correctly on my local machine !!! 
--> Something went here badly wrong
--> Maybe my problem was that I had to reinstall the azure/openai libary
--> The students forgot to add the dependency of azure/openai to the package.json aka package-lock.json
--> Do not remove package-lock from git
--> Get the package-lock.json and package,json from the students reposetories
----

## Describtion

## How to use the VSCode Plugin

## Dependencies

- "@azure/openai": "^1.0.0-beta.12"
- openai@^4.0.0

## Installing Dependencies & Build

# MCDC-Backend

The MCDC-Backend provides a streamlined solution for machine-to-machine client-server interactions. Below, you'll find details on dependencies, how to utilize the backend, and installation instructions.

## Dependencies

- Flask==3.0.2
- Flask-RESTful==0.3.10
- flask_cors==4.0.0
- gunicorn==21.2.0
- Additional dependencies required by the **py-mcdc** framework.

## Installing Dependencies & Build

The MCDC-Backend requires initial setup. We recommend using Debian-based systems (e.g., Ubuntu, Mint). Firstly, follow the steps outlined in the **"Installing Dependencies & Build"** section of the **py-mcdc** repository. Typically, this process includes installing Flask dependencies. However, ensure that Flask==3.0.2, flask-RESTful==0.3.10, flask_cors==4.0.0, and gunicorn==21.2.0 are installed via the Python package manager.

Once installed, navigate to the `mcdc_test` directory and execute `python3 app.py`. Please note that depending on your Python installation, it may be either `python3` or `python`.

Alternatively, you can use Docker for a simplified setup. Install Docker Desktop or the Docker Engine on your local machine ([Docker install guide for Ubuntu](https://docs.docker.com/engine/install/ubuntu/) or [Docker install guide for Windows](https://docs.docker.com/desktop/install/windows-install/)).

### Docker
Navigate to the base directory containing the `Dockerfile` and run: `docker build -t mcdc_test_backend .` to locally build the Docker image. Then, execute `docker run -p 5000:5000 mcdc_test_backend` to start the container. The endpoints should now be accessible via `"your_address":5000/"your_endpoint"`. Using Docker can simplify the setup process for the mcdc_test framework.

## How to Use the MCDC_Backend

The MCDC-Backend offers multiple endpoints for interaction, with two main ones:

- /AnlayseExp - HTTP-Request-Method(s):
  - GET: Provides a description of the POST-Request for expression analysis.
  - POST: Returns all MCDC states for a given expression.

- /AnlayseMultiExp
  - GET: Describes the POST-Request for analyzing multiple expressions.
  - POST: Returns MCDC states for any number of expressions that the server can handle.

Additionally, the following endpoints offer basic functionality:
- /Documentation - HTTP-Request-Method(s):
  - GET: Provides a brief overview of the API ENDPOINTS.
- /ExampleRequest  - HTTP-Request-Method(s):
  - GET: Returns predefined MCDC-States for testing, based on a specified expression.
- /delete/logs - HTTP-Request-Method(s):
  - GET: Retrieves the current log file.
  - DELETE: Deletes and resets the current log file.

Access these endpoints at "YOUR_SERVER_IP:5000". Sample requests can be found in the `postman_api_examples` directory.

# py-mcdc
This project aims at generating test cases satisfying modified condition decision coverage (MC/DC) criterion based on reduced ordered decision diagrams (roBDDs).
We propose different heuristics for selection of test cases based on longest paths in the roBDDs and all of them maximize the reuse factor:
- longest paths and reuse factor as a natural number (<img src="https://render.githubusercontent.com/render/math?math=\mathcal{H}_{LPN}">)
- longest paths and reuse factor as a Boolean number (<img src="https://render.githubusercontent.com/render/math?math=\mathcal{H}_{LPB}">)
- longest paths which may merge and reuse factor as a natural number (<img src="https://render.githubusercontent.com/render/math?math=\mathcal{H}_{LMMN}">) 
- longest paths which may merge and reuse factor as a Boolean number (<img src="https://render.githubusercontent.com/render/math?math=\mathcal{H}_{LMMB}">) 
- longest paths with better size (<img src="https://render.githubusercontent.com/render/math?math=\mathcal{H}_{LPBS}">)

 The following is our setup framework:

![](./setupframework.jpg)

Our setup takes as input the roBDD for a given decision, the number of permutations, and the number of runs. 
That is every heuristic is applied for a number of permutations of the order of the conditions and we repeat a run on a given permutation,
exploring different random choices within the equivalent best pairs.
The selection method refers to the different heuristics proposed.
The benchmarks refer to the specifications written as Boolean expressions (decisions).
Here you can find the [TCAS II decisions](https://github.com/selabhvl/py-mcdc/blob/main/mcdc_test/tcasii.py).
MC/DC test specifications are the meaning of what is MC/DC in the context of roBDDs and three values logic.
We consider the reuse factor in our MC/DC analysis to reuse as much as possible the existing selected TCs.
Finally, we produce n MC/DC pairs as output for each decision with the size of n+m solutions.

## Dependencies
- python 3.8 (minimum)
- pyeda library
- Graphviz packages

## Installing Dependencies & Build
- Install the Python3 "development" package.

  For Debian-based systems (eg Ubuntu, Mint):

  `sudo apt-get install python3-dev`

  For RedHat-based systems (eg RHEL, Centos):

   `sudo yum install python3-devel`

- Install the dependencies:
   `pip3 install -r requirements.txt`

- Install the Graphviz packages (useful when you want to visualize roBDDs): 
    
    ```
    apt-get update
    apt-get install graphviz*
    ```
 
<!--
- Install latest release pyeda version using pip:

   `pip3 install pyeda`

- Install pyeda from the repository:
  
  Clone the pyeda library:

  `git clone git://github.com/cjdrake/pyeda.git`
-->

- Build
  ```
  python3 setup.py clean --all
  python3 setup.py build
  python3 setup.py install --force --user
  ```

## Generating BDDs 

- To generate a BDD for a Boolean expression
    ```
    # python3
    >>> from pyeda.inter import *
    >>> from graphviz import Source
    >>> a, b, c, d, e= map(bddvar, 'abcde')
    >>> f=a & (~b | ~c) & d | e
    >>> gv = Source(f.to_dot())
    >>> gv.render('Example1', view=True)
    ```
## Generating MC/DC test cases from an roBDD
- Clone this library:

  `git clone https://github.com/selabhvl/py-mcdc.git`

- Generate MC/DC test cases from the command line (for TCAS II specifications)

  `python3 mcdc_test/pathsearch.py "number of permutations" "number of runs"`

- Example for 5040 order permutations and 6 runs (It takes very long time for high number of permutations, You can use few number permutations to try it first (for example 5)):

  `python3 mcdc_test/pathsearch.py 5040 6`
- To generate curves with GNUplot:
  ```
  gnuplot -p 'generated file.plot' 
  ```

- Example: 
  ```
  gnuplot -p 'VS-LongestBool.11-5040-6.plot'
  ```
### Result:
The figure below shows the probability distribution of n+m solutions generated using longest paths and reuse factor as a Boolean number (<img src="https://render.githubusercontent.com/render/math?math=\mathcal{H}_{LPB}">).
The labels indicate the decision number in the [TCAS II decisions](https://github.com/selabhvl/py-mcdc/blob/main/mcdc_test/tcasii.py) and the number of conditions contained in that specific decision.
For example 1:6 means the first decision contains 6 conditions. The closer the curves are to the top left the more the n+1 solutions.

![](./LPB.png)