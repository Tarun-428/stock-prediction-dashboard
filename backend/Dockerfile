# Use slim Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system deps (if you need yfinance, pandas, etc.)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# Copy backend source code
COPY . .

# Expose backend port
EXPOSE 5000

# Run Flask app (ensure app.run(host="0.0.0.0", port=5000) is set)
CMD ["python", "app.py"]
