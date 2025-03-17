import torch  # ✅ Ensure PyTorch is imported
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from ultralytics import YOLO
import os
import traceback
import glob

app = Flask(__name__)
CORS(app)

# ✅ Ensure correct paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
RESULTS_FOLDER = os.path.join(BASE_DIR, "results")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# ✅ Lazy-load YOLO model (don't load at startup)
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")
model = None

@app.route("/")
def home():
    return "Flask API is running. Use /predict to send images."

@app.route("/predict", methods=["POST"])
def predict():
    global model
    try:
        if model is None:
            print("🔄 Loading YOLO Model on CPU...")
            model = YOLO(MODEL_PATH, device="cpu", verbose=False)  # ✅ Force CPU
            print("✅ YOLO Model Loaded Successfully!")

        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        filename = file.filename
        img_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(img_path)

        # ✅ Run YOLO detection (memory optimized)
        results = model(img_path, conf=0.6, save=False)  # ✅ Save=False saves memory

        # ✅ Extract detected disease name
        detected_disease = "Unknown Disease"
        for result in results:
            for box in result.boxes:
                detected_disease = result.names[int(box.cls[0])]

        # ✅ Minimal disease info (reduce memory)
        disease_details = {
            "cause": "Unknown",
            "treatment": "Unknown",
            "prevention": "Unknown",
        }

        return jsonify({
            "message": detected_disease,
            "disease_info": disease_details
        }), 200

    except Exception as e:
        print("Error in /predict:", str(e))
        traceback.print_exc()
        return jsonify({"error": f"Detection failed: {str(e)}"}), 500

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))  # Default to 5000 if PORT is not set
    app.run(host="0.0.0.0", port=PORT)
