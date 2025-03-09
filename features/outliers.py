from flask import Blueprint, jsonify, request, send_file
import os
import pandas as pd
from features.utils import detect_outliers, generate_boxplot

outliers_bp = Blueprint('outliers', __name__)
DATA_FILE = "current_df.pkl"

def load_dataframe():
    """ Load DataFrame from pickle file if it exists. """
    if not os.path.exists(DATA_FILE):
        return None, {"error": f"File '{DATA_FILE}' not found."}, 404
    df = pd.read_pickle("current_df.pkl")
    if df.empty:
        return None, {"error": "Loaded DataFrame is empty."}, 400
    return df, None, None

@outliers_bp.route('/detect-outliers', methods=['GET'])
def get_outliers():
    df, error_response, error_code = load_dataframe()
    if error_response:
        return jsonify(error_response), error_code
    return detect_outliers(df)

@outliers_bp.route('/get-boxplot', methods=['POST'])
def get_boxplot():
    df, error_response, error_code = load_dataframe()
    if error_response:
        return jsonify(error_response), error_code

    data = request.get_json()
    column = data.get('column')

    if not column or column not in df.columns:
        return jsonify({"error": "Invalid or missing column name"}), 400

    return generate_boxplot(df, column)

@outliers_bp.route('/filter-outliers', methods=['POST'])
def filter_outliers():
    df, error_response, error_code = load_dataframe()
    if error_response:
        return jsonify(error_response), error_code

    data = request.get_json()
    column = data.get('column')
    min_value = data.get('min_value')
    max_value = data.get('max_value')

    if column not in df.columns:
        return jsonify({"error": "Invalid column"}), 400

    try:
        min_value = float(min_value) if min_value != "none" else None
        max_value = float(max_value) if max_value != "none" else None
    except (TypeError, ValueError):
        return jsonify({"error": "Min and Max values must be valid numbers or 'none'"}), 400

    # Apply filters only if min/max values are provided
    if min_value is not None and max_value is not None:
        filtered_df = df[(df[column] >= min_value) & (df[column] <= max_value)]
    elif min_value is not None:
        filtered_df = df[df[column] >= min_value]
    elif max_value is not None:
        filtered_df = df[df[column] <= max_value]
    else:
        filtered_df = df  # No filtering applied

    filtered_df.to_pickle("current_df.pkl")  
    return jsonify({"message": "Data filtered and saved", "filtered_rows": filtered_df.shape[0]}), 200


@outliers_bp.route('/get-columns', methods=['GET'])
def get_columns():
    try:
        df = pd.read_pickle("current_df.pkl")
        print("Columns:", df.columns.tolist())  # Debugging statement
        print("DataFrame shape:", df.shape)  # Print shape for verification
        return jsonify({"columns": df.columns.tolist()}), 200
    except Exception as e:
        print(f"Error loading DataFrame: {e}")
        return jsonify({"error": "Failed to load DataFrame"}), 500


@outliers_bp.route('/outlier-values', methods=['GET'])
def outlier_values():
    df, error_response, error_code = load_dataframe()
    if error_response:
        return jsonify(error_response), error_code
    return detect_outliers(df)
