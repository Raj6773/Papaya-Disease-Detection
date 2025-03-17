# ✅ Use a lightweight Python image
FROM python:3.9-slim  

# ✅ Install system dependencies for OpenCV & YOLO
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*  

# ✅ Set environment variables
ENV MPLCONFIGDIR=/tmp  
ENV YOLO_CONFIG_DIR=/tmp  

# ✅ Set working directory
WORKDIR /app  

# ✅ Copy necessary files
COPY requirements.txt .  
COPY app.py .  
COPY best.pt .  

# ✅ Install dependencies
RUN pip install --no-cache-dir -r requirements.txt  

# ✅ Expose the port
EXPOSE 5000  

# ✅ Use Gunicorn for production
gunicorn -b 0.0.0.0:5000 --workers=2 --timeout 120 app:app
