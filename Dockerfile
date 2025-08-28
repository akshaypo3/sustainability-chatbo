# Use official Python image
FROM python:3.11-slim

WORKDIR /app

# Copy only dependency files first (build cache)
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source
COPY . .

EXPOSE 8000

# Start FastAPI (ensure 'main.py' and 'app' exist)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
