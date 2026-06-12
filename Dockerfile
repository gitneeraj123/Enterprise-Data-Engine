FROM python:3.11-slim

# Install system dependencies needed for pgvector/psycopg2 and PDF processing
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency definitions
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose ports for Streamlit and Airflow
EXPOSE 8501 8080