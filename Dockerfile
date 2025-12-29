# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
# ripgrep is added for faster code search (rg command)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependency definitions
COPY requirements.txt .

# Install packages
RUN pip install --no-cache-dir -r requirements.txt

# NOTE: We DO NOT copy the application code here because it is massive (200GB+).
# It will be mounted via docker-compose volumes.

# Expose port 8000
EXPOSE 8000

# Set environment variables
ENV PROJECT_ROOT=/app
ENV PYTHONUNBUFFERED=1

# Run the server
CMD ["python", "deployment/server.py"]
