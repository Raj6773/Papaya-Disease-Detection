# Use a lightweight Python image
FROM python:3.9-slim  

# Install dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*  

# Set environment variables  
ENV MPLCONFIGDIR=/tmp  
ENV YOLO_CONFIG_DIR=/tmp  

# Set working directory
WORKDIR /app  

# Copy files  
COPY backend/requirements.txt .  
COPY backend/app.py .  
COPY backend/best.pt .  

# Install dependencies  
RUN pip install --no-cache-dir -r requirements.txt  

# Expose the Flask API port
EXPOSE 5000  

# Run Flask API  
CMD ["python", "app.py"]
