# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app will run on
EXPOSE 10000

# Define environment variable
ENV PYTHONUNBUFFERED 1

# Run the Flask app using Gunicorn with a 300s timeout
CMD ["gunicorn", "--timeout", "300", "-w", "4", "-b", "0.0.0.0:10000", "app:app"]
