FROM python:3.8-slim
LABEL Lukas Sebastian Hofmann <lukhofma@ucm.es>

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        make \
        libgmp3-dev \
        graphviz \
        python3-dev \
        pkg-config \
        && rm -rf /var/lib/apt/lists/*

# Install PySMT solver (MSat)
RUN pip install pysmt \
    && pysmt-install --check \
    && echo "yes" | pysmt-install --confirm-agreement --msat

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app
RUN pip3 install --no-cache-dir -e .

ENV FLASK_APP=/app/mcdc_test/app.py \
    FLASK_ENV=production \
    PYTHONPATH=/app/mcdc_test

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--no-debugger"]