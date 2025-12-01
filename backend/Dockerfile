# backend/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps (needed for numpy, pandas, xgboost, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Expose backend port
EXPOSE 5000

# Run Flask app (app.py must have app.run(host="0.0.0.0", port=5000))
CMD ["python", "app.py"]
