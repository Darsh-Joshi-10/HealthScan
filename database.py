from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    symptoms = db.Column(db.Text, nullable=True)
    diagnosis = db.Column(db.String(50), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)

    def __init__(self, name, dob, age, gender, symptoms, diagnosis, filepath):
        self.name = name
        self.dob = dob
        self.age = age
        self.gender = gender
        self.symptoms = symptoms
        self.diagnosis = diagnosis
        self.filepath = filepath
