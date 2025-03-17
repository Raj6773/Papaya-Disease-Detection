from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from ultralytics import YOLO
import os
import traceback
import glob

app = Flask(__name__)
CORS(app)

# ✅ Ensure paths work inside Docker
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
RESULTS_FOLDER = os.path.join(BASE_DIR, "results")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# ✅ Lazy-load YOLO model only when needed
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")
model = None  # Do not load at startup

@app.route("/")
def home():
    return "Flask API is running. Use /predict to send images."

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK"}), 200

@app.route("/predict", methods=["POST"])
def predict():
    global model
    try:
        if model is None:
            print("🔄 Loading YOLO Model...")
            model = YOLO(MODEL_PATH)  # Load model at first request
            print("✅ YOLO Model Loaded Successfully!")

        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        filename = file.filename
        img_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(img_path)

        # Run YOLO detection
        results = model(img_path, save=True, project=RESULTS_FOLDER, name="predict")

        # ✅ Find latest prediction folder dynamically
        prediction_folders = glob.glob(os.path.join(RESULTS_FOLDER, "predict*"))
        latest_folder = max(prediction_folders, key=os.path.getctime)
        output_img_path = os.path.join(latest_folder, filename)

        # ✅ Extract detected disease name
        detected_disease = "Unknown Disease"
        for result in results:
            for box in result.boxes:
                detected_disease = result.names[int(box.cls[0])]

        disease_details = {
            "cause": "Not a disease.",
            "treatment": "No treatment needed.",
            "prevention": "No prevention needed.",
        }

        if os.path.exists(output_img_path):
            return jsonify({
                "message": detected_disease,
                "image_url": f"/download/{filename}",
                "disease_info": disease_details
            }), 200
        else:
            raise FileNotFoundError(f"Output image not found at {output_img_path}")

    except Exception as e:
        print("Error in /predict:", str(e))
        traceback.print_exc()
        return jsonify({"error": f"Detection failed: {str(e)}"}), 500

@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    prediction_folders = glob.glob(os.path.join(RESULTS_FOLDER, "predict*"))
    latest_folder = max(prediction_folders, key=os.path.getctime)
    output_img_path = os.path.join(latest_folder, filename)

    if os.path.exists(output_img_path):
        return send_file(output_img_path, mimetype="image/jpeg")
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 5000))  # ✅ Change for Railway (no fixed port)
    app.run(host="0.0.0.0", port=PORT)
