import os
from flask import Flask,Blueprint, render_template,url_for, jsonify,send_file, Response,send_from_directory
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from features.mv_model import visualize_spider_chart,analyze_missing_data,visualize_missing_data,visualize_distributions,visualize_relationships
from features.utils import generate_missing_values_plot
from weasyprint import HTML
import glob
from sklearn.preprocessing import LabelEncoder
import io
import tempfile



smartimp_bp = Blueprint('smartim', __name__)

@smartimp_bp.route('/smart_imputation', methods=['GET'])
def smart_imputation_analysis():
    try:
        if not os.path.exists('current_df.pkl'):
            return jsonify({"error": "Dataset not found. Please upload a file first."}), 404
        
        df = pd.read_pickle('current_df.pkl')
        print("Dataset loaded successfully. Columns:", df.columns.tolist())
        
        if df.empty:
            return jsonify({"error": "The dataset is empty."}), 400
        
        # Track missing values in categorical columns
        categorical_cols = df.select_dtypes(exclude=['int64', 'float64']).columns.tolist()
        for col in categorical_cols:
            df[f'{col}_missing'] = df[col].isna()  # Create a flag for missing values
        
        # Fill missing values in categorical columns with a placeholder
        for col in categorical_cols:
            df[col] = df[col].fillna('Unknown')
        # Encode categorical columns
        label_encoders = {}
        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))  # Encode categorical columns
            label_encoders[col] = le  # Store the encoder
        
        # Reintroduce missing values after encoding
        for col in categorical_cols:
            df.loc[df[f'{col}_missing'], col] = np.nan  # Reintroduce missing values
        
        # Ensure all columns are numeric
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        for col in numerical_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert everything to numeric
        
        print("NaN values in numerical columns:", df[numerical_cols].isna().sum())
        
        # Perform missing data analysis
        suggestions = analyze_missing_data(df)
        print("Missing data analysis completed. Suggestions:", suggestions)
        
        # Generate visualizations using only numeric data
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        static_folder = os.path.join('static', 'images')
        os.makedirs(static_folder, exist_ok=True)
        
        def try_visualize(func, path):
            try:
                func(numeric_df, path)  # Pass only numeric data
                print(f"Generated: {path}")
            except Exception as e:
                print(f"Failed to generate {path}: {str(e)}")
        
        heatmap_path = os.path.join(static_folder, 'missing_data_heatmap.png')
        try_visualize(visualize_missing_data, heatmap_path)
        
        correlation_matrix_path = os.path.join(static_folder, 'correlation_matrix.png')
        try_visualize(visualize_relationships, correlation_matrix_path)
        
        spider_chart_path = os.path.join(static_folder, 'spider_chart.png')
        try_visualize(lambda df, p: visualize_spider_chart(suggestions, p), spider_chart_path)
        
        try:
            visualize_distributions(numeric_df, static_folder)  # Pass only numeric data
            print("Distribution plots generated.")
        except Exception as e:
            print("Failed to generate distribution plots:", str(e))
        
        # Render the results template
        distribution_images = sorted(glob.glob(os.path.join(static_folder, '*_distribution.png')))
        web_image_paths = format_image_paths()
        pdf_image_paths = {k: f"file://{os.path.abspath(v)}" if isinstance(v, str) else [f"file://{os.path.abspath(img)}" for img in v] for k, v in web_image_paths.items()}
        
        return render_template('results.html', 
                              num_rows=len(df), 
                              num_cols=len(df.columns), 
                              suggestions=suggestions, 
                              numerical_cols=numerical_cols,
                              web_images=web_image_paths,
                              pdf_images=pdf_image_paths)
    
    except Exception as e:
        print("Error generating report:", str(e))
        return jsonify({"error": f"Error generating report: {str(e)}"}), 500

@smartimp_bp.route('/generate_report', methods=['GET'])
def generate_report():
    try:
        if not os.path.exists('current_df.pkl'):
            return jsonify({"error": "Dataset not found. Please upload a file first."}), 404
        
        df = pd.read_pickle('current_df.pkl')

        # Prepare encoded DataFrame for report generation
        encoded_df = df.copy()  # Create a copy for encoding
        categorical_cols = encoded_df.select_dtypes(exclude=['int64', 'float64']).columns.tolist()
        for col in categorical_cols:
            le = LabelEncoder()
            encoded_df[col] = le.fit_transform(encoded_df[col].astype(str))  # Encode categorical columns

        suggestions = analyze_missing_data(encoded_df)  # Use encoded DataFrame for suggestions
        web_images = format_image_paths()

        rendered_html = render_template(
            'results.html',
            num_rows=len(encoded_df),
            num_cols=len(encoded_df.columns),
            suggestions=suggestions,
            numerical_cols=encoded_df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
            web_images=web_images
        )
        adjusted_html = adjust_image_paths(rendered_html)  # Adjust image paths here
        
        # Use WeasyPrint to generate the PDF
        pdf_bytes = HTML(string=adjusted_html).write_pdf()

        # Create a temporary file for the PDF
        temp_dir = tempfile.gettempdir()
        report_filename = 'report_analysis.pdf'  # Changed filename for the report
        report_path = os.path.join(temp_dir, report_filename)
        
        with open(report_path, 'wb') as report_file:
            report_file.write(pdf_bytes)
        
        return jsonify({"message": "Report generated successfully!", "filename": report_filename}), 200

    except Exception as e:
        return jsonify({"error": f"Error generating PDF: {str(e)}"}), 500

@smartimp_bp.route('/download/<report_filename>', methods=['GET'])
def download(report_filename):
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, report_filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404


def format_image_paths():
    """Returns dictionary of web-friendly image paths."""
    distribution_images = sorted(glob.glob(os.path.join('static', 'images', '*_distribution.png')))
    
    return {
        "heatmap": url_for('static', filename='images/missing_data_heatmap.png'),
        "correlation_matrix": url_for('static', filename='images/correlation_matrix.png'),
        "spider_chart": url_for('static', filename='images/spider_chart.png'),
        "distributions": [url_for('static', filename=f'images/{os.path.basename(img)}') for img in distribution_images],    
    }


            
STATIC_IMAGES_PATH = os.path.abspath("C:/Users/user/Documents/Projects/ToDeploy/NeatData/static/images")

def adjust_image_paths(html_content):
    """Replace web image paths with absolute local paths for PDF rendering."""
    static_images_path = os.path.join(os.getcwd(), "static", "images")
    for img in os.listdir(static_images_path):
        if img.endswith(".png"):
            web_path = f'src="{url_for("static", filename=f"images/{img}")}"'
            local_path = f'src="file:///{os.path.join(static_images_path, img)}"'
            html_content = html_content.replace(web_path, local_path)
    return html_content

