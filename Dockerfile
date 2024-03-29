FROM python:3.11-slim-buster

WORKDIR /app

ENV FLASK_APP=yugiwebapp.py 
ENV FLASK_RUN_HOST=0.0.0.0 

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 3000

CMD ["python", "yugiwebapp.py"]
