from flask import Blueprint, jsonify, request,json,send_file
import pandas as pd
import numpy as np
import os
from io import BytesIO
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler



utile_bp = Blueprint('utile', __name__)
###Pairplot:
def visualise_dimension(df):
    """
    Selects up to 6 columns for visualization, generates a pairplot, and returns data types and the image path.
    """
    if df.shape[1] > 6:
        df = df.iloc[:, :6]
    
    data_types = df.dtypes.apply(lambda x: x.name).to_dict()
    pairplot_path = 'pairplot.png'
    generate_pairplot(df, os.path.join('static', 'images', pairplot_path))
    
    return data_types, pairplot_path

def generate_pairplot(df, save_path):
    """
    Generates and saves a pairplot for the given DataFrame.
    """
    if df.empty:
        raise ValueError("DataFrame is empty, cannot generate pairplot")
    
    sns.pairplot(df)
    plt.savefig(save_path, dpi=100)
    plt.close()

def generate_custom_pairplot(df, save_path, plot_color, plot_width, plot_height):
    """
    Generates a custom pairplot with styling and saves it to the specified path.
    """
    if df.empty:
        raise ValueError("DataFrame is empty, cannot generate custom pairplot")
    if not save_path:
        raise ValueError("Invalid save_path provided")
    if df.shape[1] > 6:
        df = df.iloc[:, :6]
    
    sns.set(style="ticks")
    plot = sns.pairplot(
        df,
        plot_kws={'color': plot_color},
        height=plot_height / 2,  # Adjust height for subplots
        aspect=plot_width / plot_height  # Adjust aspect ratio
    )
    
    for ax in plot.axes.flatten():
        if hasattr(ax, 'collections'):
            for coll in ax.collections:
                coll.set_edgecolor(plot_color)
                coll.set_facecolor(plot_color)
        if hasattr(ax, 'patches'):
            for patch in ax.patches:
                patch.set_edgecolor(plot_color)
                patch.set_facecolor(plot_color)
        ax.set_xlabel(ax.get_xlabel(), fontsize=12)
        ax.set_ylabel(ax.get_ylabel(), fontsize=12)
        for label in ax.get_xticklabels():
            label.set_rotation(45)
    
    plot.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()
##standrise:

def normalize(df):
    """
    Normalize the DataFrame using standardization (mean=0, std=1).
    """
    scaler = StandardScaler()
    normalized_data = scaler.fit_transform(df)
    return pd.DataFrame(normalized_data, columns=df.columns)

###MV:
def generate_missing_data_table(missing_stats, missing_percentage, data_types):
    table = pd.DataFrame({
        'Column': list(missing_stats.keys()),
        'Missing Values': list(missing_stats.values()),
        'Missing Percentage': list(missing_percentage.values()),
        'Data Type': list(data_types.values())
    })
    return table.to_html(classes='data', header="true", index=False)

def generate_missing_values_plot(df, save_path, color_map, plot_width, plot_height, missing_color, present_color):
    plt.figure(figsize=(plot_width, plot_height), dpi=100)
    cmap = sns.color_palette([present_color, missing_color], as_cmap=True)
    sns.heatmap(df.isnull(), cbar=False, cmap=cmap)
    plt.title('Missing Values Heatmap')
    handles = [plt.Line2D([0], [0], color=present_color, lw=4, label='Present'),
                plt.Line2D([0], [0], color=missing_color, lw=4, label='Missing')]
    plt.legend(handles=handles, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.savefig(save_path, bbox_inches='tight') 
    plt.close()
    

def visualize_missing_values(df, missing_color='#000000', present_color='#FFFFFF'):
    missing_stats = df.isnull().sum().to_dict()
    missing_percentage = (df.isnull().sum() / len(df) * 100).to_dict()
    data_types = df.dtypes.apply(lambda x: x.name).to_dict()
    sample_data = df.head().to_html(classes='data', header="true")
    os.makedirs('static/images', exist_ok=True)
    missing_values_plot = 'missing_values_plot.png'
    save_path = os.path.join('static', 'images', missing_values_plot)
    generate_missing_values_plot(df, save_path, 'viridis', 8, 6, missing_color, present_color)
    return missing_stats, missing_percentage, data_types, sample_data, missing_values_plot

###OUTLIERS:


def generate_boxplot(df, column):
    if df is None:
        return jsonify({"error": "No dataset uploaded"}), 400
    if column not in df.columns:
        return jsonify({"error": "Invalid column"}), 400
    plt.figure(figsize=(8, 6))
    boxplot = plt.boxplot(df[column].dropna(), 
                            patch_artist=True, 
                            boxprops=dict(facecolor='skyblue', color='black'),
                            medianprops=dict(color='red'),
                            whiskerprops=dict(color='black'),
                            capprops=dict(color='black'),
                            flierprops=dict(markerfacecolor='red', marker='o', markersize=6))
    plt.title(f'Boxplot of {column}', fontsize=14)
    plt.ylabel(column, fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    mean = df[column].mean()
    plt.axhline(mean, color='green', linestyle='--', label='Mean')
    plt.legend()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return send_file(buf, mimetype='image/png')

def detect_outliers(df):
    if df is None:
        return jsonify({"error": "No dataset uploaded"}), 400
    outlier_data = {}
    outlier_columns = []
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        if not outliers.empty:
            outlier_columns.append(col)
            outlier_data[col] = outliers[col].tolist()
    return jsonify({
        "outlier_columns": outlier_columns,
        "outliers_values": outlier_data
    })