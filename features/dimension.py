from flask import Blueprint, jsonify, request, json
import pandas as pd
import numpy as np
import os
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPRegressor
from features.mv_model import visualize_relationships
from features.utils import generate_custom_pairplot, normalize, visualise_dimension

dimension_bp = Blueprint("dimension", __name__)
DATA_FILE = "current_df.pkl"


def load_dataframe():
    """ Load DataFrame from pickle file if it exists. """
    if not os.path.exists(DATA_FILE):
        return None, {"error": f"File '{DATA_FILE}' not found."}, 404
    df = pd.read_pickle(DATA_FILE)
    if df.empty:
        return None, {"error": "Loaded DataFrame is empty."}, 400
    return df, None, None

@dimension_bp.route("/dimension", methods=["POST"])
def dimension():
    try:
        df, error_response, error_code = load_dataframe()
        if error_response:
            return jsonify(error_response), error_code
        print("DataFrame shape:", df.shape)
        print("DataFrame columns:", df.columns)
        data = request.json
        print("Input data:", data)
        choice = data.get("choice")
        target_variable = data.get("target")
        exclude_numeric = data.get("exclude_numeric", "")
        exclude_categorical = data.get("exclude_categorical", "")

        if isinstance(exclude_numeric, list):
            exclude_numeric = ",".join(exclude_numeric)
        if isinstance(exclude_categorical, list):
            exclude_categorical = ",".join(exclude_categorical)
        exclude_numeric = exclude_numeric.split(",")
        exclude_categorical = exclude_categorical.split(",")
        try:
            num_features = int(data.get("num_features", 5))
            hidden_layer_size = int(data.get("hidden_layer_size", 10))
            max_iter = int(data.get("max_iter", 1000))
        except ValueError:
            return jsonify({"error": "Invalid integer input for numerical parameters."}), 400
        cols_to_exclude = [col for col in exclude_numeric + exclude_categorical if col in df.columns]
        if target_variable and target_variable in cols_to_exclude:
            cols_to_exclude.remove(target_variable)
        df.drop(columns=cols_to_exclude, errors="ignore", inplace=True)
        if choice != "1" and target_variable and target_variable not in df.columns:
            return jsonify({"error": f"Target variable '{target_variable}' not found in dataset."}), 400
        df = df.select_dtypes(include=[np.number])
        if df.isnull().values.any():
            nan_columns = df.columns[df.isnull().any()].tolist()
            return jsonify({"error": f"Data contains NaN values in columns: {', '.join(nan_columns)}"}), 400
        if choice != "1":  # PCA does not require a target variable
            if not target_variable:
                return jsonify({"error": "Target variable is required for this method."}), 400
            X = df.drop(columns=[target_variable])
            y = df[target_variable]
        else:  
            X = df  
            y = None
        print("Shape of X:", X.shape)
        if y is not None:
            print("Shape of y:", y.shape)
        if y is not None and X.shape[0] != y.shape[0]:
            return jsonify({"error": "Feature set and target variable must have the same number of rows."}), 400
        normalized_data = normalize(X) 
        result = None
        transformed_df = None

        if choice == "1":  # PCA
            result, transformed_df = apply_pca(normalized_data)
        elif choice == "2":  # RFE
            result, transformed_df = apply_rfe(normalized_data, y, num_features, df)
        elif choice == "3":  # AEFS
            result, transformed_df = apply_aefs(normalized_data, y, num_features, hidden_layer_size, max_iter, df)
        else:
            return jsonify({"error": "Invalid choice"}), 400
        transformed_df.to_pickle('current_df.pkl')
        print("Transformed DataFrame saved to 'current_df.pkl'")
        print(transformed_df.head())
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Error processing data: {str(e)}"}), 500


def apply_rfe(X, y, num_features, df):
    """ Perform Recursive Feature Elimination (RFE). """
    try:
        model = LogisticRegression()
        rfe = RFE(estimator=model, n_features_to_select=num_features)
        rfe.fit(X, y)
        selected_features = X.columns[rfe.support_]
        print("RFE support mask:", rfe.support_)
        print("Feature names:", X.columns)
        print("Shape of X:", X.shape)
        print("Selected features:", selected_features)
        transformed_df = df[selected_features].copy()  # Create a new DataFrame with selected features
        transformed_df['target'] = y.values  # Add target column to the DataFrame

        # Return the result and the transformed DataFrame
        return (
            {
                "message": "RFE transformation completed successfully.",
                "selected_features": selected_features.tolist(),
            },
            transformed_df,
        )
    except Exception as e:
        raise Exception(f"Error during RFE: {str(e)}")


def apply_pca(normalized_data):
    """ Perform PCA and return results. """
    try:
        model = PCA()
        reduced_data = model.fit_transform(normalized_data)
        explained_variance = model.explained_variance_ratio_
        cumulative_variance = np.cumsum(explained_variance)
        optimal_components = np.argmax(cumulative_variance >= 0.80) + 1
        transformed_df = pd.DataFrame(reduced_data[:, :optimal_components], columns=[f"PC{i+1}" for i in range(optimal_components)])
        return (
            {
                "explained_variance": explained_variance.tolist(),
                "cumulative_variance": cumulative_variance.tolist(),
                "chosen_components": int(optimal_components),
                "message": f"PCA chose {optimal_components} components explaining {round(cumulative_variance[optimal_components - 1] * 100, 2)}% of variance.",
                "visualization_data": {
                    "components": list(range(1, len(explained_variance) + 1)),
                    "explained_variance": explained_variance.tolist(),
                    "cumulative_variance": cumulative_variance.tolist(),
                    "optimal_components": int(optimal_components),
                },
            },
            transformed_df,
        )
    except Exception as e:
        raise Exception(f"Error during PCA: {str(e)}")

def apply_aefs(normalized_data, y, num_features, hidden_layer_size, max_iter, df):
    try:
        normalized_data = np.array(normalized_data)
        if num_features > normalized_data.shape[1]:
            raise ValueError("num_features cannot exceed the number of available features.")
        model = MLPRegressor(hidden_layer_sizes=(hidden_layer_size,), max_iter=max_iter, random_state=42)
        model.fit(normalized_data, normalized_data)
        weights = model.coefs_[0]
        feature_importance = np.linalg.norm(weights, axis=1)
        selected_feature_indices = np.argsort(feature_importance)[-num_features:]
        selected_features = df.columns[selected_feature_indices].tolist()
        reduced_data = normalized_data[:, selected_feature_indices]
        transformed_df = pd.DataFrame(reduced_data, columns=selected_features)
        transformed_df['target'] = y 
        return ({"message": "AEFS transformation completed successfully.", "selected_features": selected_features}, transformed_df)
    except Exception as e:
        raise Exception(f"Error during AEFS: {str(e)}")
    
    
@dimension_bp.route("/dimension_overview", methods=["GET"])
def dimension_overview():
    """ Provides an overview of the dataset. """
    try:
        df, error_response, error_code = load_dataframe()
        if error_response:
            return jsonify(error_response), error_code
        data_types, pairplot_path = visualise_dimension(df)
        os.makedirs("static/images", exist_ok=True)
        correlation_path = os.path.join("images", "correlation_matrix.png")
        save_path = os.path.join("static", correlation_path)
        visualize_relationships(df, save_path)
        return jsonify(
            {
                "data_types": df.dtypes.apply(lambda x: x.name).to_dict(),
                "correlation": correlation_path,
                "pairplot_path": pairplot_path,
                "data": df.fillna("").values.tolist(),
            }
        )
    except Exception as e:
        return jsonify({"error": f"Error retrieving data overview: {str(e)}"}), 500


@dimension_bp.route("/customize_pairplot", methods=["POST"])
def customize_pairplot():
    """ Customizes and generates a pairplot. """
    try:
        df, error_response, error_code = load_dataframe()
        if error_response:
            return jsonify(error_response), error_code
        plot_color = request.json.get("plotColor", "#FF5733")
        plot_width = int(request.json.get("plotWidth", 6))
        plot_height = int(request.json.get("plotHeight", 4))
        if plot_width <= 0 or plot_height <= 0:
            return jsonify({"error": "Plot dimensions must be positive integers."}), 400
        pairplot_path = "custom_pairplot.png"
        generate_custom_pairplot(df, os.path.join("static", "images", pairplot_path), plot_color, plot_width, plot_height)
        return jsonify({"pairplot_path": pairplot_path})
    except Exception as e:
        return jsonify({"error": f"Error customizing plot: {str(e)}"}), 500
