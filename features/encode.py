import os
from flask import Blueprint, jsonify, request
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
import category_encoders as ce 
from sklearn.svm import SVC


encode_bp = Blueprint('encode', __name__)



@encode_bp.route('/encode', methods=['POST'])
def encode_data():
    try:
        df = pd.read_pickle('current_df.pkl')
        encoding_choice = request.json.get('encoding_choice')
        columns = request.json.get('encoding_columns').split(',')
        columns = [col.strip() for col in columns]

        if encoding_choice == 'onehot':
            df = pd.get_dummies(df, columns=columns)
        elif encoding_choice == 'label':
            le = LabelEncoder()
            for col in columns:
                df[col] = le.fit_transform(df[col])
        elif encoding_choice == 'binary':
            encoder = ce.BinaryEncoder(cols=columns)
            df = encoder.fit_transform(df)
        elif encoding_choice == 'manual':
            manual_mappings = request.json.get('manual_mappings')
            for col, mappings in manual_mappings.items():
                df[col] = df[col].map(mappings).fillna(df[col])

        df.to_pickle('current_df.pkl')
        sample_data_after = df.head().to_html(classes='data', header="true")
        return jsonify({"message": "Encoding applied successfully.", "sample_data_after": sample_data_after})
    except Exception as e:
        return jsonify({"error": f"Encoding failed. Potential causes: {str(e)}"}), 500

@encode_bp.route('/encoding_overview', methods=['GET'])
def encoding_overview():
    try:
        df = pd.read_pickle('current_df.pkl')
        print("DataFrame loaded successfully.")
        print(df.head())  # Ensure the data exists

        data_types, column_categories, sample_data = get_encoding_overview(df)
        
        print("Returning data types:", data_types)
        print("Returning categories:", column_categories)

        return jsonify({
            "data_types": data_types,
            "column_categories": column_categories,
            "sample_data": sample_data
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"Error retrieving encoding overview: {str(e)}"}), 500

def get_encoding_overview(df):
    data_types = df.dtypes.apply(lambda x: x.name).to_dict()
    column_categories = {col: df[col].unique().tolist() for col in df.select_dtypes(include=['object']).columns}
    sample_data = df.sample(max(10, len(df))).head(15).to_html(classes='data', header="true")
    return data_types, column_categories, sample_data
