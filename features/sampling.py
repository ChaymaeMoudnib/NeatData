from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sampling_bp = Blueprint('sampling', __name__)

def convert_to_serializable(obj):
    if isinstance(obj, pd.Series):
        return obj.to_dict()
    if isinstance(obj, (np.integer, np.int64, np.int32, np.int16)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        return float(obj)
    if isinstance(obj, (np.ndarray, pd.Index)):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    return obj


@sampling_bp.route('/sampling_overview', methods=['GET'])
def sampling_overview():
    try:
        if not os.path.exists('current_df.pkl'):
            raise FileNotFoundError('current_df.pkl')

        df = pd.read_pickle('current_df.pkl')
        data_types = df.dtypes.apply(lambda x: x.name).to_dict()

        missing_values = (df.isnull().sum() / len(df) * 100).to_dict()
        duplicate_rows = int(df.duplicated().sum())

        data_info = {
            "Number of Rows": int(len(df)),
            "Number of Columns": int(len(df.columns)),
            "Missing Values": missing_values,
            "Duplicate Rows": duplicate_rows
        }

        data_types = convert_to_serializable(data_types)
        data_info = convert_to_serializable(data_info)

        return jsonify({"data_types": data_types, "data_info": data_info})
    except Exception as e:
        return jsonify({"error": f"Error retrieving data overview: {str(e)}"}), 500

@sampling_bp.route('/sample_data', methods=['POST'])
def sample_data():
    try:
        if not os.path.exists('current_df.pkl'):
            raise FileNotFoundError('current_df.pkl')

        df = pd.read_pickle('current_df.pkl')

        sampling_method = request.json.get('samplingMethod')
        sample_size = request.json.get('sampleSize')
        stratify_column = request.json.get('stratifyColumn')
        num_clusters = request.json.get('numClusters')
        cluster_column = request.json.get('clusterColumn')

        sample_size = int(sample_size) if sample_size else 0
        num_clusters = int(num_clusters) if num_clusters else 0

        if sampling_method == 'simple_random':
            sampled_df = df.sample(n=sample_size)
        elif sampling_method == 'stratified':
            stratified_size = sample_size / len(df)
            sampled_df = df.groupby(stratify_column, group_keys=False).apply(lambda x: x.sample(frac=stratified_size, replace=stratified_size > 1))
        elif sampling_method == 'systematic':
            step = len(df) // sample_size
            sampled_df = df.iloc[::step, :]
        elif sampling_method == 'cluster':
            clusters = df.sample(n=num_clusters)
            sampled_df = df[df[cluster_column].isin(clusters[cluster_column])]
        elif sampling_method == 'convenience':
            sampled_df = df.head(sample_size)
        else:
            return jsonify({"error": f"Invalid sampling method: {sampling_method}"}), 400

        sampled_df = sampled_df.head(10)

        analysis_results = {
            "mean": sampled_df.mean().apply(convert_to_serializable).to_dict(),
            "median": sampled_df.median().apply(convert_to_serializable).to_dict(),
            "std": sampled_df.std().apply(convert_to_serializable).to_dict(),
            "var": sampled_df.var().apply(convert_to_serializable).to_dict(),
            "min": sampled_df.min().apply(convert_to_serializable).to_dict(),
            "max": sampled_df.max().apply(convert_to_serializable).to_dict(),
            "quartiles": {
                "Q1": sampled_df.quantile(0.25).apply(convert_to_serializable).to_dict(),
                "Q2": sampled_df.quantile(0.5).apply(convert_to_serializable).to_dict(),
                "Q3": sampled_df.quantile(0.75).apply(convert_to_serializable).to_dict()
            }
        }

        sampling_errors = {
            "sampling_error": convert_to_serializable(calculate_sampling_error(df, sampled_df)),
            "selection_error": convert_to_serializable(calculate_selection_error(df, sampled_df)),
            "non_response_error": {"rate": convert_to_serializable(calculate_non_response_error(df, sampled_df))}
        }

        return jsonify({
            "sampled_data": sampled_df.applymap(convert_to_serializable).to_dict(orient='list'),
            "analysis_results": analysis_results,
            "errors": sampling_errors
        })
    except Exception as e:
        return jsonify({"error": f"Error sampling data: {str(e)}"}), 500

def calculate_sampling_error(df, sampled_df):
    population_mean = df.mean()
    sample_mean = sampled_df.mean()
    sampling_error = (sample_mean - population_mean) / population_mean * 100
    return sampling_error.to_dict()

def calculate_selection_error(df, sampled_df):
    population_distribution = df.describe().to_dict()
    sample_distribution = sampled_df.describe().to_dict()
    selection_error = {}
    for col in population_distribution:
        if col in sample_distribution:
            selection_error[col] = {
                "population_std": population_distribution[col]["std"],
                "sample_std": sample_distribution[col]["std"],
                "selection_bias": (sample_distribution[col]["std"] - population_distribution[col]["std"]) / population_distribution[col]["std"] * 100
            }
    return selection_error

def calculate_non_response_error(df, sampled_df):
    non_response_rate = (len(df) - len(sampled_df)) / len(df) * 100
    return {"non_response_rate": non_response_rate}

# def create_visualizations(sampled_df):
#     visualizations = {
#         "correlation_matrix": "correlation_matrix.png",
#         "pairplot": "pairplot.png"
#     }
#     sns.pairplot(sampled_df)
#     plt.savefig(os.path.join('static', visualizations["pairplot"]))
#     plt.close()
#     plt.figure(figsize=(10, 8))
#     sns.heatmap(sampled_df.corr(), annot=True, cmap='coolwarm')
#     plt.savefig(os.path.join('static', visualizations["correlation_matrix"]))
#     plt.close()
#     return visualizations
