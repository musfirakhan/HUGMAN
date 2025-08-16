# Use Python 3.9 as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p generated_characters output animations

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=animations/web_server.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5001

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "Starting HUGMAN Character Generation System..."\n\
echo "================================================"\n\
echo "Starting web server on port 5001..."\n\
python animations/web_server.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set the default command
CMD ["/app/start.sh"]
