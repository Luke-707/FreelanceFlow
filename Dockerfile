# Base image
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (needed for Pillow/image processing)
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

# Ensure necessary directories exist and have permissions
RUN mkdir -p /app/db_data /app/staticfiles && chmod 777 /app/db_data /app/staticfiles

# Expose the Django port
EXPOSE 8000

# Default command to start the server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
