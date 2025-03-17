# ✅ Use a lightweight Python image
FROM python:3.9-slim  

# ✅ Install system dependencies (for OpenCV, Ultralytics)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*  

# ✅ Set environment variables  
ENV MPLCONFIGDIR=/tmp  
ENV YOLO_CONFIG_DIR=/tmp  

# ✅ Set working directory (Root, not inside `/backend`)
WORKDIR /app  

# ✅ Copy necessary files  
COPY backend/requirements.txt .  
COPY backend/app.py .  
COPY backend/best.pt .  

# ✅ Install dependencies  
RUN pip install --no-cache-dir -r requirements.txt  

# ✅ Expose port for Railway  
EXPOSE 5000  

# ✅ Run Flask app directly
CMD ["python", "app.py"]
