# Use official Python image
FROM python:3.11-slim

WORKDIR /app

# Copy only dependency files first (build cache)
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source
COPY . .

# Expose the port KServe/Knative expects
EXPOSE 8080

# Start FastAPI on 0.0.0.0:8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
