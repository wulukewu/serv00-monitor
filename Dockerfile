# Use the official Playwright Python image
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies (requests)
# Note: Playwright is already installed in the base image
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Chromium is installed
RUN playwright install chromium

# Copy the script
COPY monitor.py .

# Run the script
CMD ["python", "monitor.py"]