FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../shared /app/agents/shared
COPY main.py /app/agents/nexus/main.py

CMD ["uvicorn", "agents.nexus.main:app", "--host", "0.0.0.0", "--port", "8080"]
