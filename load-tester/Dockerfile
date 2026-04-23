FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy locustfile
COPY locustfile.py .

# Default command - can be overridden when running
CMD ["locust", "-f", "locustfile.py", "--host=http://api-gateway:8000"]
