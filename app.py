from main import generate
from flask import Flask, request, jsonify, render_template, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
import pytesseract
from ocr import extract_text
import csv
import os
import pandas as pd
from datetime import datetime
import io
import pdfkit
import uuid
from nlp import recommend_sections
import json

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crime_reports.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# CrimeReport model
class CrimeReport(db.Model):
    firNo = db.Column(db.String, primary_key=True)
    district = db.Column(db.String)
    date = db.Column(db.Date)
    day = db.Column(db.String)
    dateOfOccurrence = db.Column(db.Date)
    placeOfOccurrence = db.Column(db.String)
    name = db.Column(db.String)
    dob = db.Column(db.Date)
    nationality = db.Column(db.String)
    occupation = db.Column(db.String)
    address = db.Column(db.String)
    reportedCrime = db.Column(db.String)
    propertiesInvolved = db.Column(db.String)
    modelOutput = db.Column(db.String)

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/report-crime")
def reportCrime():
    return render_template("report-crime.html")

@app.route('/process_reported_crime', methods=['POST'])
def process_reported_crime():
    try:
        data = request.get_json()

        reported_crime = data.get('reportedCrime', '')
        properties_involved = data.get('propertiesInvolved', '')
        combined_text = f"{reported_crime} {properties_involved}"

        ipc_matches, bns_matches = recommend_sections(combined_text)

        import json
        model_output = json.dumps({
            "ipc": ipc_matches,
            "bns": bns_matches
        })

        new_report = CrimeReport(
            firNo=data.get('firNo'),
            district=data.get('district'),
            date=datetime.strptime(data.get('date'), '%Y-%m-%d'),
            day=data.get('day'),
            dateOfOccurrence=datetime.strptime(data.get('dateOfOccurrence'), '%Y-%m-%d'),
            placeOfOccurrence=data.get('placeOfOccurrence'),
            name=data.get('name'),
            dob=datetime.strptime(data.get('dob'), '%Y-%m-%d'),
            nationality=data.get('nationality'),
            occupation=data.get('occupation'),
            address=data.get('address'),
            reportedCrime=reported_crime,
            propertiesInvolved=properties_involved,
            modelOutput=model_output
        )

        db.session.add(new_report)
        db.session.commit()

        return jsonify({'result': {"ipc": ipc_matches, "bns": bns_matches}, 'status': 'success'})
    except Exception as e:
        print(f"Error processing crime report: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/submit_ipc_sections', methods=['POST'])
def submit_ipc_sections():
    data = request.get_json()
    fir_no = data.get('firNo')
    ipc_sections = data.get('ipcSections')

    # Update the IPC sections
    report = CrimeReport.query.filter_by(firNo=fir_no).first()
    if report:
        report.modelOutput = ipc_sections
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'IPC sections updated successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Report not found'}), 404

@app.route('/ipc-dataset')
def ipcDataset():
    csv_file_path = 'static/resources/ipc_ds.csv'
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)
            data = list(csv_reader)
    except FileNotFoundError:
        return "CSV file not found."
    return render_template('ipc-dataset.html', headers=headers, data=data)

@app.route("/ocr-analysis")
def ocrCrimeAnalysis():
    return render_template("ocr-recognition.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"})

        file = request.files['file']
        file_type = request.form.get('fileType', '').lower()

        if file.filename == '':
            return jsonify({"error": "No selected file"})

        # Validate file type
        allowed_types = ['image', 'pdf']
        if file_type not in allowed_types:
            return jsonify({"error": "Invalid file type"})

        # Ensure uploads directory exists
        upload_dir = 'uploads'
        os.makedirs(upload_dir, exist_ok=True)

        # Create unique filename to avoid conflicts
        ext = os.path.splitext(file.filename)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        temp_path = os.path.join(upload_dir, unique_filename)

        # Save the file temporarily
        file.save(temp_path)

        # Extract text using OCR
        extracted_text = extract_text(temp_path)

        # Generate additional output if needed
        generated_output = generate(extracted_text)

        # Clean up the temp file
        os.remove(temp_path)

        return jsonify({
            "message": extracted_text,
            "generated_output": generated_output
        })

    except Exception as e:
        print(f"Error uploading file: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/fir-form")
def firForm():
    return render_template("fir-form.html")

@app.route('/display_fir/<string:fir_no>')
def display_fir(fir_no):
    report = CrimeReport.query.filter_by(firNo=fir_no).first()
    if report:
        # Initialize with empty defaults
        model_data = {
            "ipc": {},
            "bns": {}
        }

        # Parse stored modelOutput if it exists and is valid
        try:
            stored_output = json.loads(report.modelOutput) if report.modelOutput else {}
            # If it's already a dict with ipc/bns, great!
            if isinstance(stored_output, dict):
                model_data["ipc"] = stored_output.get("ipc", [])
                model_data["bns"] = stored_output.get("bns", [])
        except json.JSONDecodeError:
            pass  # Keep default empty ipc/bns if JSON is broken

        return render_template('display-report.html', report=report, model_data=model_data)
    else:
        return jsonify({'error': 'Report not found'}), 404



path_wkhtmltopdf = r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
@app.route('/download_fir_pdf/<fir_no>')
def download_fir_pdf(fir_no):
    report = CrimeReport.query.filter_by(firNo=fir_no).first()
    if report:
        # Call the recommend_sections function using the report's text
        model_data = recommend_sections(report.reportedCrime)

        # Render the HTML with both report and model_data
        rendered_html = render_template(
            'display-report.html',
            report=report,
            model_data=model_data
        )

        # Generate PDF from the rendered HTML
        pdf_content = pdfkit.from_string(
            rendered_html, 
            False, 
            options={"enable-local-file-access": ""},
            configuration=config
        )

        pdf_file = io.BytesIO(pdf_content)
        response = make_response(pdf_file.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=FIR_Report_{fir_no}.pdf'
        return response
    else:
        return 'Report not found', 404

# Ensure tables are created
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
