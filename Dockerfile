FROM ubuntu:22.04

RUN apt upgrade -y

RUN apt update -y

RUN apt install python3-pip unzip -y

RUN apt install python3.10-venv libaio1 -y

# Create a virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /usr/src/cupejobs_renew_api

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD uvicorn main:app --host=0.0.0.0 --port=${CUPEJOBS_PORT}