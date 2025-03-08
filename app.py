import re
import os
import logging
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import time
import subprocess
from threading import Thread
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy np
import ollama  # For report generation via Ollama API
from database import db, Patient

# Initialize Flask app
app = Flask(__name__)

# Configure database (SQLite for simplicity; swap for PostgreSQL/MySQL in production)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthscan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# File upload settings
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load the TensorFlow model (ensure the model file exists at the specified path)
MODEL_PATH = 'models/pneumonia_detection_model.h5'
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    logging.info("Model loaded successfully.")
except Exception as e:
    logging.error(f"Failed to load model from {MODEL_PATH}: {e}")
    exit(1)

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize the database (create tables if they don't exist)
with app.app_context():
    db.create_all()

# Utility: Check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Utility: Calculate age from date of birth
def calculate_age(dob):
    today = datetime.today()
    birthdate = datetime.strptime(dob, '%Y-%m-%d')
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

# Preprocess image for the model
def preprocess_image(img_path):
    try:
        img = image.load_img(img_path, target_size=(150, 150))  # Adjust target size as needed
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        img_array = img_array / 255.0  # Normalize the image
        return img_array
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return None

# Predict diagnosis using the loaded model
def predict_diagnosis(img_path):
    img_array = preprocess_image(img_path)
    if img_array is None:
        return "Error processing image"
    
    prediction = model.predict(img_array)
    # Assuming the model returns a probability; adjust threshold as needed
    return "Pneumonia Detected" if prediction[0] > 0.5 else "No Pneumonia Detected"

# Utility function to process the Ollama response:
def process_report_text(text):
    # Remove any content between <think> and </think> (the model's thinking process)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Replace markdown-style bold markers with HTML bold tags
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    return text

# Route: Home page with form
@app.route('/')
def index():
    return render_template('index.html')

# Route: Analyze uploaded image and store patient data
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        patient_name = request.form.get('patient_name')
        patient_dob = request.form.get('patient_dob')
        patient_gender = request.form.get('patient_gender')
        symptoms = request.form.get('symptoms')
        image_file = request.files.get('xray_image')

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

            # Run diagnosis on the saved image
            diagnosis = predict_diagnosis(image_path)
            age = calculate_age(patient_dob)

            # Create and save a new patient record
            new_patient = Patient(
                name=patient_name,
                dob=patient_dob,
                age=age,
                gender=patient_gender,
                symptoms=symptoms,
                diagnosis=diagnosis,
                filepath=image_path
            )
            db.session.add(new_patient)
            db.session.commit()
            logging.info(f"Patient data saved: {new_patient}")

            return jsonify({
                'id': new_patient.id,
                'name': new_patient.name,
                'dob': new_patient.dob,
                'age': new_patient.age,
                'gender': new_patient.gender,
                'symptoms': new_patient.symptoms,
                'diagnosis': new_patient.diagnosis,
                'filepath': new_patient.filepath
            })
        else:
            return jsonify({'error': 'Invalid image file. Please upload a valid image.'}), 400

    except Exception as e:
        logging.error(f"Error in /analyze: {e}")
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500

# Route: Generate a professional report using Ollama (with processing)
@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        desiredModel = 'phi3:mini'
        questionToAsk = (
            "Generate a structured pneumonia report with key details in exactly 1500 words. Trim unnecessary information. Dont give useless information."
        )

        # Call the Ollama API
        response = ollama.chat(model=desiredModel, messages=[
            {
                'role': 'user',
                'content': questionToAsk,
            },
        ])

        OllamaResponse = response['message']['content']

        # Process the response to remove <think> sections and convert markdown bold to HTML <strong>
        processed_report = process_report_text(OllamaResponse)

        logging.info("Ollama Report Generated:\n" + processed_report)
        with open("OutputOllama.txt", "w", encoding="utf-8") as text_file:
            text_file.write(processed_report)

        return jsonify({'report': processed_report})
    except Exception as e:
        logging.error(f"Error generating report: {e}")
        return jsonify({'error': 'Failed to generate report.'}), 500

# Route: Retrieve all patient records
@app.route('/patients', methods=['GET'])
def get_patients():
    try:
        patients = Patient.query.all()
        patient_list = [{
            'id': p.id,
            'name': p.name,
            'dob': p.dob,
            'age': p.age,
            'gender': p.gender,
            'symptoms': p.symptoms,
            'diagnosis': p.diagnosis,
            'filepath': p.filepath
        } for p in patients]
        return jsonify(patient_list)
    except Exception as e:
        logging.error(f"Error fetching patients: {e}")
        return jsonify({'error': 'Error fetching patient data'}), 500

def get_ip_addresses():
    """Get all network interfaces IP addresses"""
    import socket
    import netifaces
    
    ips = []
    # Get all network interfaces
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                if addr['addr'] != '127.0.0.1':  # Skip localhost
                    ips.append(addr['addr'])
    return ips

if __name__ == '__main__':
    # Check if port is available
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('0.0.0.0', 8000))
        sock.close()
    except OSError:
        logging.error("Port 8000 is already in use. Please close other applications using this port.")
        exit(1)

    def run_flask():
        app.run(debug=False, host='0.0.0.0', port=8000, use_reloader=False)

    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    time.sleep(2)  # Wait for Flask to start

    # Display all available IP addresses
    ips = get_ip_addresses()
    logging.info("\n" + "="*50)
    logging.info("Server is running! Access the application using any of these URLs:")
    logging.info("Local computer:  http://localhost:8000")
    for ip in ips:
        logging.info(f"Network access: http://{ip}:8000")
    logging.info("="*50 + "\n")
    
    # Try to open in browser
    try:
        logging.info("Opening application in default browser...")
        subprocess.run(['start', 'msedge', '--app=http://localhost:8000'], shell=True, check=True)
    except Exception as e:
        try:
            subprocess.run(['start', 'chrome', '--app=http://localhost:8000'], shell=True, check=True)
        except Exception as e2:
            logging.info("Could not auto-open browser. Please use one of the URLs above.")
