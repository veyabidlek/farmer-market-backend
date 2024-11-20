# Use official Python image as a base
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY . /app

COPY wait_for_db.sh /wait_for_db.sh
RUN chmod +x /wait_for_db.sh

# Install dependencies
RUN pip install -r requirements.txt

# Expose port 8000
EXPOSE 8000
