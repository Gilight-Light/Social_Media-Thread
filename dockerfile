FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install playwright and browsers
RUN playwright install chromium

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data

EXPOSE 5000 8501

CMD ["python", "app.py"]