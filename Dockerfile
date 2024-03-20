FROM python:3.8-slim

LABEL Lukas Sebastian Hofmann <lukhofma@ucm.es>

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    make \
    libgmp3-dev \
    graphviz* \
    python3-dev

# Install PySMT solver (MSat)
RUN pip install pysmt
RUN pysmt-install --check
RUN apt-get update && apt-get install -y expect
RUN expect -c 'spawn pysmt-install --msat; expect "Continue? \[Y\]es/\[N\]o"; send "yes\n"; interact'

WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt 



COPY . /app
RUN pip3 install -e .
ENV FLASK_APP=/app/mcdc_test/app.py

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--no-debugger"]