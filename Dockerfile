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

# ✅ Set working directory INSIDE backend
WORKDIR /app/backend  

# ✅ Copy necessary files  
COPY backend/requirements.txt .  
COPY backend/app.py .  
COPY backend/best.pt .  

# ✅ Install dependencies  
RUN pip install --no-cache-dir -r requirements.txt  

# ✅ Expose the Flask API port
EXPOSE 5000  

# ✅ Use Gunicorn for production (faster & stable than `python app.py`)
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
