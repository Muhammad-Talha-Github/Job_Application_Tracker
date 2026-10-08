# Use the same Python generation as the local project environment.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies separately so Docker can reuse this layer between code edits.
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Include the FastAPI app and Alembic migration files.
COPY . .

EXPOSE 8000

# Apply migrations after PostgreSQL is healthy, then start the API on the container network.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
