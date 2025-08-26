# Use lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the code
COPY . .

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "main.py"]
