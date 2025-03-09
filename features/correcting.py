import pandas as pd
import os
from flask import Blueprint, request, jsonify, render_template

correct_bp = Blueprint('correct_bp', __name__)


@correct_bp.route('/correct', methods=['POST'])
def correct_values():
    try:
        df = pd.read_pickle('current_df.pkl')
        target_column = request.json.get("target_column")
        action = request.json.get("action")
        corrections = request.json.get("corrections", "")
        corrections_dict = {}

        if isinstance(corrections, str):
            for line in corrections.splitlines():
                if ':' in line:
                    old_value, new_value = line.split(':', 1)
                    corrections_dict[old_value.strip()] = new_value.strip()
        else:
            return jsonify({"error": "Corrections should be a string."}), 400

        table_before = df.head(10).to_dict(orient="records")

        if action == "replace":
            for old_value, new_value in corrections_dict.items():
                df[target_column] = df[target_column].replace(old_value, new_value)
        elif action == "remove":
            for old_value in corrections_dict.keys():
                df[target_column] = df[target_column].replace(old_value, '', regex=True)
        elif action == "modify_date":
            date_format = request.json.get("date_format")
            if not date_format:
                return jsonify({"error": "No date format provided"}), 400
            try:
                df[target_column] = df[target_column].astype(str)
                df[target_column] = pd.to_datetime(df[target_column], format=date_format, errors='coerce')
                df[target_column] = df[target_column].fillna("Invalid Date")
            except ValueError as ve:
                return jsonify({"error": f"Date format error: {str(ve)}"}), 400
            except Exception as e:
                return jsonify({"error": f"An error occurred: {str(e)}"}), 500

        df.to_pickle('current_df.pkl')
        table_data = df.head(10).to_dict(orient="records")

        return jsonify({
            "message": "Corrections applied successfully!",
            "table": table_data,
            "table_before": table_before,
            "ask_next": "Do you want to correct another column?"
        })
    except Exception as e:
        return jsonify({"error": f"Failed to apply corrections: {str(e)}"}), 500

@correct_bp.route('/before', methods=['POST'])
def before():
    try:
        df = pd.read_pickle('current_df.pkl')
        table_before = df.head(10).to_dict(orient="records")
        return jsonify({
            "table_before": table_before,
        })
    except Exception as e:
        return jsonify({"error": f"Failed to apply corrections: {str(e)}"}), 500


@correct_bp.route('/get_columns', methods=['GET'])
def get_columns():
    try:
        df = pd.read_pickle('current_df.pkl')
        return jsonify({"columns": df.columns.tolist()})
    except Exception as e:
        return jsonify({"error": f"Failed to load columns: {str(e)}"}), 500
