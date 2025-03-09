from flask import Blueprint, jsonify, request, current_app
import os
import pandas as pd
from pymongo import MongoClient
from io import BytesIO

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    target_column = request.form.get('target_column')  

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        try:
            filename = file.filename
            upload_folder = current_app.config.get('UPLOAD_FOLDER', './uploads')
            os.makedirs(upload_folder, exist_ok=True)  
            file_extension = filename.rsplit('.', 1)[1].lower()
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            csv_file_path = file_path.rsplit('.', 1)[0] + '.csv'
            if file_extension == 'xlsx':
                try:
                    df = pd.read_excel(file_path)
                    df.to_csv(csv_file_path, index=False)
                    os.remove(file_path)  # Remove the original XLSX file
                except Exception as e:
                    return jsonify({"error": f"Excel file conversion failed: {str(e)}"}), 500
            else:
                csv_file_path = file_path  

            try:
                df = pd.read_csv(csv_file_path)
                if df.shape[1] == 1:
                    df = pd.read_csv(csv_file_path, delimiter=';')

            except Exception as e:
                return jsonify({"error": f"Failed to read CSV file: {str(e)}"}), 500

            if target_column and target_column not in df.columns:
                return jsonify({"error": f"Target column '{target_column}' not found in dataset"}), 400
            df.to_pickle('current_df.pkl') 
            return jsonify({"message": "Data loaded successfully.", "columns": list(df.columns)})
        except Exception as e:
            return jsonify({"error": f"File processing failed: {str(e)}"}), 500

    return jsonify({"error": "Only CSV and XLSX files are allowed."}), 400
