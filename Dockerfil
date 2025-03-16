# Use official Python image
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV MPLCONFIGDIR=/tmp
ENV YOLO_CONFIG_DIR=/tmp

# Set working directory
WORKDIR /app

# Copy files
COPY backend/app.py .
COPY backend/best.pt .
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Run Flask app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
