# HealthScan - Pneumonia Detection System

A Flask-based web application that uses machine learning to detect pneumonia from chest X-rays and generate medical reports.

## Features

- Pneumonia detection from X-ray images
- Patient data management
- Automated report generation using Ollama
- Network-accessible interface
- Browser-based UI

## Prerequisites

- Python 3.8+
- TensorFlow 2.x
- Flask
- Ollama
- Required Python packages:
  ```bash
  pip install flask tensorflow numpy netifaces werkzeug ollama
  ```

## Project Structure

```
/D:/Major Proj/
├── app.py              # Main application file
├── database.py         # Database models
├── models/            
│   └── pneumonia_detection_model.h5  # ML model (not in repo)
├── uploads/            # Patient images (not in repo)
├── templates/          # HTML templates
└── static/            # CSS, JS, and other static files
```

## Setup

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies
4. Place your trained model in `models/pneumonia_detection_model.h5`
5. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. Access the application:
   - Local: `http://localhost:8000`
   - Network: Check console for IP addresses
2. Upload X-ray image
3. Fill in patient details
4. View results and generated report

## Security Notes

- Not configured for production use
- Requires proper security measures before deployment
- Patient data should be handled according to healthcare regulations

## Files Not in Repository

- `uploads/*`: Patient X-ray images
- `models/pneumonia_detection_model.h5`: ML model
- `healthscan.db`: Patient database
- Environment files and credentials
