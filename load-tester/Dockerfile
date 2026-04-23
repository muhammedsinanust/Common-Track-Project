FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy locustfile
COPY locustfile.py .

# Default command - hits auth-service directly (no gateway)
CMD ["locust", "-f", "locustfile.py", "--host=http://auth-service:8001"]
