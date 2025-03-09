import os
from flask import Flask,Blueprint, render_template,url_for, jsonify, Response,send_from_directory
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from features.mv_model import visualize_spider_chart,analyze_missing_data,visualize_missing_data,visualize_distributions,visualize_relationships
import pdfkit
import glob
from sklearn.preprocessing import LabelEncoder
import io



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
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=['int64', 'float64']).columns.tolist()
        label_encoders = {}
        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))  # Convert to string first to handle NaNs
            label_encoders[col] = le  # Store the encoder
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        for col in numerical_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert everything to numeric
        print("NaN values in numerical columns:", df[numerical_cols].isna().sum())
        suggestions = analyze_missing_data(df)
        print("Missing data analysis completed. Suggestions:", suggestions)
        static_folder = os.path.join('static', 'images')
        os.makedirs(static_folder, exist_ok=True)
        def try_visualize(func, path):
            try:
                func(df, path)
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
            visualize_distributions(df, static_folder)
            print("Distribution plots generated.")
        except Exception as e:
            print("Failed to generate distribution plots:", str(e))
        distribution_images = sorted(glob.glob(os.path.join(static_folder, '*_distribution.png')))
        web_image_paths = format_image_paths()
        pdf_image_paths = {k: f"file://{os.path.abspath(v)}" if isinstance(v, str) else [f"file://{os.path.abspath(img)}" for img in v] for k, v in web_image_paths.items()}
        return render_template('results.html', 
                                num_rows=len(df), 
                                num_cols=len(df.columns), 
                                suggestions=suggestions, 
                                numerical_cols=df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
                                web_images=web_image_paths,
                                pdf_images=pdf_image_paths)
    except Exception as e:
        print("Error generating report:", str(e))
        return jsonify({"error": f"Error generating report: {str(e)}"}), 500

def format_image_paths():
    """Returns dictionary of web-friendly image paths."""
    distribution_images = sorted(glob.glob(os.path.join('static', 'images', '*_distribution.png')))
    
    return {
        "heatmap": url_for('static', filename='images/missing_data_heatmap.png'),
        "correlation_matrix": url_for('static', filename='images/correlation_matrix.png'),
        "spider_chart": url_for('static', filename='images/spider_chart.png'),
        "distributions": [url_for('static', filename=f'images/{os.path.basename(img)}') for img in distribution_images]
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


@smartimp_bp.route('/download_report')
def download_report():
    try:
        if not os.path.exists('current_df.pkl'):
            return jsonify({"error": "Dataset not found. Please upload a file first."}), 404
        
        df = pd.read_pickle('current_df.pkl')
        suggestions = analyze_missing_data(df)
        web_images = format_image_paths()

        rendered_html = render_template(
            'results.html',
            num_rows=len(df),
            num_cols=len(df.columns),
            suggestions=suggestions,
            numerical_cols=df.select_dtypes(include=['int64', 'float64']).columns.tolist(),
            web_images=web_images
        )

        adjusted_html = adjust_image_paths(rendered_html)  # Adjust image paths here

        config = pdfkit.configuration(wkhtmltopdf=r"C:\wkhtmltopdf\bin\wkhtmltopdf.exe")
        options = {'enable-local-file-access': ''}

        pdf_bytes = pdfkit.from_string(adjusted_html, False, configuration=config, options=options)
        pdf_io = io.BytesIO(pdf_bytes)
        return Response(
            pdf_io.getvalue(),
            mimetype='application/pdf',
            headers={"Content-Disposition": "attachment; filename=analysis_report.pdf"}
        )
    except Exception as e:
        return jsonify({"error": f"Error generating PDF: {str(e)}"}), 500



