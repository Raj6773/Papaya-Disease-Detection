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
ENV PORT=7860  # ✅ Set correct Hugging Face port  

# ✅ Set working directory INSIDE backend
WORKDIR /app/backend  

# ✅ Copy necessary files  
COPY backend/requirements.txt .  
COPY backend/app.py .  
COPY backend/best.pt .  

# ✅ Install dependencies  
RUN pip install --no-cache-dir -r requirements.txt  

# ✅ Expose the correct port for Hugging Face  
EXPOSE 7860  

# ✅ Use Gunicorn for production, increase timeout  
CMD ["gunicorn", "-b", "0.0.0.0:7860", "--timeout", "600", "app:app"]
