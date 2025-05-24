# Use Python 3.12 slim as the base image
FROM python:3.12-slim as python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        nodejs \
        npm \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Install Node.js dependencies and build Tailwind CSS
COPY package*.json ./
RUN npm install
COPY static_src/styles/input.css ./static_src/styles/
RUN npm run watch:tailwind

# Copy project files
COPY . .

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Collect static files
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the entrypoint script
CMD ["/app/entrypoint.sh"] 