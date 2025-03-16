from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from ultralytics import YOLO
import os
import traceback
import glob

app = Flask(__name__)
CORS(app)

# Load YOLO model
MODEL_PATH = r"C:\Users\rajki\Downloads\mini\best.pt"
model = YOLO(MODEL_PATH)

UPLOAD_FOLDER = "uploads"
RESULTS_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Disease Information Dictionary
disease_info = {
    "Anthracnose_Leaf": {
        "cause": "Caused by Colletotrichum fungus, spreads in warm, humid conditions.",
        "treatment": "Apply fungicides like copper or mancozeb. Remove infected leaves.",
        "prevention": "Ensure good air circulation, avoid overhead watering, and maintain field hygiene."
    },
    "BacterialSpot_Leaf": {
        "cause": "Caused by Xanthomonas bacteria, often due to high humidity.",
        "treatment": "Use copper-based bactericides, remove infected leaves.",
        "prevention": "Avoid overhead watering, improve drainage, and use resistant plant varieties."
    },
    "Curl_Leaf": {
        "cause": "Caused by virus or environmental stress such as poor nutrition.",
        "treatment": "Provide balanced fertilizers, prune affected leaves.",
        "prevention": "Ensure proper irrigation, pest control, and use resistant varieties."
    },
    "RingSpot_Leaf": {
        "cause": "Caused by Papaya Ringspot Virus (PRSV), spread by aphids.",
        "treatment": "Remove infected plants, use virus-resistant varieties.",
        "prevention": "Control aphids using neem oil or insecticidal soap."
    },
    "Anthracnose_Fruit": {
        "cause": "Fungal infection that thrives in high humidity.",
        "treatment": "Apply post-harvest fungicides and store fruits in cool conditions.",
        "prevention": "Avoid fruit injuries, practice good field sanitation, and use resistant varieties."
    },
    "BlackSpot_Fruit": {
        "cause": "Caused by Asperisporium caricae fungus, worsens in high humidity.",
        "treatment": "Use fungicides like copper oxychloride.",
        "prevention": "Ensure proper spacing between plants, improve air circulation."
    },
    "RingSpot_Fruit": {
        "cause": "Papaya Ringspot Virus affecting fruit appearance.",
        "treatment": "Remove infected plants, control aphids.",
        "prevention": "Plant virus-resistant varieties, use insecticidal soap."
    },
    "Phytophthora_Fruit": {
        "cause": "Caused by Phytophthora fungus due to excessive moisture.",
        "treatment": "Apply systemic fungicides like metalaxyl.",
        "prevention": "Improve drainage, avoid water stagnation."
    },
    "PowderyMildew_Fruit": {
        "cause": "Caused by fungal spores in dry, warm conditions.",
        "treatment": "Apply sulfur-based fungicides, prune affected areas.",
        "prevention": "Avoid excess nitrogen fertilizers, keep plants well-spaced."
    }
}

@app.route('/')
def home():
    return "Flask API is running. Use /predict to send images."

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files['image']
        filename = file.filename
        img_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(img_path)

        # Run YOLO detection
        results = model(img_path, save=True, project=RESULTS_FOLDER, name="predict")

        # Find latest prediction folder dynamically
        prediction_folders = glob.glob(os.path.join(RESULTS_FOLDER, "predict*"))
        latest_folder = max(prediction_folders, key=os.path.getctime)
        output_img_path = os.path.join(latest_folder, filename)

        # Extract detected disease name
        detected_disease = "Unknown Disease"
        for result in results:
            for box in result.boxes:
                detected_disease = result.names[int(box.cls[0])]  # Get class name

        # Get disease details if available
        disease_details = disease_info.get(detected_disease, {
            "cause": "not a disease.",
            "treatment": "no treatment needed.",
            "prevention": "no prevention needed."
        })

        if os.path.exists(output_img_path):
            return jsonify({
                "message": detected_disease,
                "image_url": f"http://{request.host}/download/{filename}",
                "disease_info": disease_details
            }), 200
        else:
            raise FileNotFoundError(f"Output image not found at {output_img_path}")

    except Exception as e:
        print("Error in /predict:", str(e))
        traceback.print_exc()
        return jsonify({"error": f"Detection failed: {str(e)}"}), 500

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    prediction_folders = glob.glob(os.path.join(RESULTS_FOLDER, "predict*"))
    latest_folder = max(prediction_folders, key=os.path.getctime)
    output_img_path = os.path.join(latest_folder, filename)

    if os.path.exists(output_img_path):
        return send_file(output_img_path, mimetype='image/jpeg')
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
