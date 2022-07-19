FROM ghcr.io/multi-py/python-gunicorn-uvicorn:py3.10-slim-LATEST
ENV MODULE_NAME="dijon.main"

# required for bsdiff4 to pip install
RUN apt-get update && apt-get install -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# get latest pip and poetry. poetry generates a requirements.txt, pip installs the requirements.txt
RUN pip install --upgrade pip
RUN pip install poetry==1.1.8 uvicorn[standard]==0.15.0 gunicorn==20.1.0 fastapi==0.68.1

# this script runs automatically at start
COPY ./prestart.sh /app/

# generate requirements.txt and install it to the system python
COPY ./pyproject.toml ./poetry.lock /app/
RUN poetry export -o requirements.txt && pip install -r requirements.txt && rm -f requirements.txt

# add the app and install it to the system python
COPY ./dijon /app/dijon
RUN pip install .
