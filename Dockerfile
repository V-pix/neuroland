FROM python:3.7-slim

WORKDIR /app

ENV PYTHONUNBUFFERED 1

RUN pip3 install --upgrade pip

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY neuroland/ .

CMD ["gunicorn", "neuroland.wsgi:application", "--bind", "0:8001"] 
