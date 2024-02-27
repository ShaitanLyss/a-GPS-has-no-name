FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

# Make port 80 available to the world outside this container
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
