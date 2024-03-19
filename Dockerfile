FROM python:3.8-slim

LABEL Lukas Sebastian Hofmann <lukhofma@ucm.es>

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    make \
    libgmp3-dev

# Install Python dependencies
RUN pip install pysmt

# Install PySMT solver (MSat)
RUN pysmt-install --check
RUN apt-get update && apt-get install -y expect
RUN expect -c 'spawn pysmt-install --msat; expect "Continue? \[Y\]es/\[N\]o"; send "yes\n"; interact'

RUN apt-get install -y python3-dev
RUN apt-get update
RUN apt-get install -y graphviz*

RUN mkdir /mcdc
WORKDIR /mcdc
COPY requirements.txt /mcdc
RUN pip3 install -r requirements.txt 

COPY . mcdc_test/ 
ENV FLASK_APP=/mcdc/mcdc_test/app.py

EXPOSE 5000
WORKDIR /mcdc/mcdc_test
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--no-debugger"]
#python3 app.py
#["flask", "run", "--host=0.0.0.0", "--port=5000", "--no-debugger"]