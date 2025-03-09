from flask import Blueprint, jsonify, request
import os
import pandas as pd
import matplotlib.pyplot as plt

visualise_bp = Blueprint('visualise', __name__)

@visualise_bp.route('/visualise', methods=['POST'])
def visualize():
    data = request.json
    filename = data['filename']  
    filepath = os.path.join('uploads', filename)  
    df = pd.read_csv(filepath)
    columns = data.get('columns', '').split(',')
    chart_type = data['chartType']
    chart_width = int(data['chartWidth'])
    chart_height = int(data['chartHeight'])
    bg_color = data['backgroundColor']
    line_color = data['lineColor']
    if not all(col in df.columns for col in columns):
        return jsonify({'error': 'Invalid columns specified'}), 400
    plt.figure(figsize=(chart_width / 100, chart_height / 100), facecolor=bg_color)
    if chart_type == 'line':
        for col in columns:
            plt.plot(df[col], label=col, color=line_color)
    elif chart_type == 'bar':
        df[columns].plot(kind='bar', color=line_color)
    elif chart_type == 'scatter' and len(columns) == 2:
        plt.scatter(df[columns[0]], df[columns[1]], color=line_color)
    elif chart_type == 'pie' and len(columns) == 1:
        plt.pie(df[columns[0]].value_counts(), labels=df[columns[0]].value_counts().index, autopct='%1.1f%%')
    elif chart_type == 'histogram':
        df[columns].plot(kind='hist', bins=20, alpha=0.7)

    plt.legend()
    plt.tight_layout()
    output_path = os.path.join('uploads', 'visualization.png')
    plt.savefig(output_path)
    plt.close()

    return jsonify({'imagePath': output_path})
