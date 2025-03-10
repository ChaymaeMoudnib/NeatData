from flask import Flask, Blueprint, request, jsonify, send_file
import os
import pandas as pd
import tempfile  # Import the tempfile module

save_bp = Blueprint('save', __name__)

@save_bp.route('/save', methods=['POST'])
def save():
    try:
        data = request.get_json()
        file_format = data.get('file_format')
        filename = data.get('filename')

        if not file_format or not filename:
            return jsonify({"error": "Missing required information"}), 400

        # Get a valid temp directory (works on Windows, Linux, and Mac)
        temp_dir = tempfile.gettempdir()
        save_path = os.path.join(temp_dir, f"{filename}.{file_format}")

        # Load the DataFrame (assuming it exists)
        df = pd.read_pickle('current_df.pkl')

        # Save file in the selected format
        save_methods = {
            'xlsx': lambda path: df.to_excel(path, index=False),
            'csv': lambda path: df.to_csv(path, index=False),
            'json': lambda path: df.to_json(path, orient='records', indent=2),
            'parquet': lambda path: df.to_parquet(path, index=False),
            'html': lambda path: df.to_html(path, index=False),
            'xml': lambda path: df.to_xml(path, index=False),
        }

        if file_format in save_methods:
            save_methods[file_format](save_path)
        else:
            return jsonify({"error": f"Unsupported file format: {file_format}"}), 400

        # Construct the download URL
        download_url = f"/download/{filename}.{file_format}"

        return jsonify({
            "message": f"File saved successfully! <a href='{download_url}' download>Click here to download</a>",
            "download_url": download_url
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500


@save_bp.route('/download/<filename>', methods=['GET'])
def download(filename):
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404
