from flask import Blueprint, jsonify, request
import os
import pandas as pd


save_bp=Blueprint('save',__name__)
@save_bp.route('/save', methods=['POST'])
def save():
    try:
        print("Raw request data:", request.data)
        data = request.get_json()  # Correct way to get JSON data
        # Debugging: Print the parsed JSON data
        print("Parsed JSON data:", data)
        file_format = data.get('file_format')
        save_path = data.get('save_path')
        filename = data.get('filename')
        custom_path = data.get('custom_path')  # For custom paths
        print("Received data:", data)
        if not file_format or not save_path or not filename:
            return jsonify({"error": "Missing required information"}), 400
        if save_path in ['documents', 'downloads', 'desktop']:
            user_home = os.path.expanduser("~")
            save_path = os.path.join(user_home, save_path.capitalize())
        elif save_path == 'custom' and custom_path:
            save_path = custom_path
        else:
            return jsonify({"error": "Invalid save path or missing custom path"}), 400
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        df = pd.read_pickle('current_df.pkl')
        full_path = os.path.join(save_path, f"{filename}.{file_format}")
        if file_format == 'xlsx':
            df.to_excel(full_path, index=False)
        elif file_format == 'csv':
            df.to_csv(full_path, index=False)
        elif file_format == 'json':
            df.to_json(full_path, orient='records', indent=2)
        elif file_format == 'parquet':
            df.to_parquet(full_path, index=False)
        elif file_format == 'html':
            df.to_html(full_path, index=False)
        elif file_format == 'xml':
            df.to_xml(full_path, index=False)
        else:
            return jsonify({"error": f"Unsupported file format: {file_format}"}), 400

        return jsonify({"message": f"File saved successfully at {full_path}"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500
    
    
    
    
    
