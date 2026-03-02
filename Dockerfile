FROM python:3.11-slim

WORKDIR /app

# Install dependencies first — Docker layer caching means this only
# re-runs when requirements.txt changes, not on every code change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Model gets mounted as a volume in development,
# baked in for production builds
COPY models/ ./models/

EXPOSE 8000

# Uvicorn with reload for dev — override in prod
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
