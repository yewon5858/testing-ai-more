FROM python:3.8-slim

LABEL Lukas Sebastian Hofmann <lukhofma@ucm.es>

# Install system dependencies
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#     gcc \
#     make \
#     libgmp3-dev \
#     graphviz \
#     python3-dev \
#     expect && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libgmp3-dev \
    graphviz \
    python3-dev \
    pkg-config

RUN pip install pysmt
RUN pysmt-install --check
RUN echo "yes" | pysmt-install --confirm-agreement --msat

WORKDIR /app
COPY requirements.txt /app
RUN pip3 install --no-cache-dir -r requirements.txt 

COPY . /app
RUN pip3 install --no-cache-dir -e .

ENV FLASK_APP=/app/mcdc_test/app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app/mcdc_test

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--no-debugger"]