FROM python:3.8.0
WORKDIR /app

RUN apt-get update && apt-get install -y vim
COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY messages.py /app/

CMD python messages.py
