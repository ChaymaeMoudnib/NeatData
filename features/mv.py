from flask import Blueprint, jsonify, request
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, KNNImputer, SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow import keras
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from features.utils import  generate_missing_data_table,generate_missing_values_plot,visualize_missing_values
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

print(tf.config.list_physical_devices('GPU'))


mv_bp = Blueprint('mv', __name__)
@mv_bp.route('/process', methods=['POST'])
def process_data():
    try:
        # Debugging: Check if the file exists
        if not os.path.exists('current_df.pkl'):
            return jsonify({"error": "File 'current_df.pkl' not found"}), 404

        df = pd.read_pickle('current_df.pkl')
        data = request.json

        print("Received Data:", data)  # Debugging

        choice = data.get('choice')
        columns = data.get('columns', '').split(',')
        columns = [col.strip() for col in columns]
        impute_choice = data.get('impute_choice')
        impute_params = data.get('impute_params', {})

        print(f"Choice: {choice}, Columns: {columns}, Impute Choice: {impute_choice}, Impute Params: {impute_params}")  # Debugging

        columns_with_missing = df.columns[df.isnull().any()].tolist()

        if 'all' in columns:
            columns = columns_with_missing
        else:
            invalid_columns = [col for col in columns if col not in df.columns]
            if invalid_columns:
                return jsonify({"error": f"Invalid columns: {invalid_columns}"}), 400

        if choice == '1':
            df.dropna(subset=columns, inplace=True)
        elif choice == '2':
            df.drop(columns=columns, inplace=True)
        elif choice == '3' and impute_choice:
            if impute_choice == 'mean_median_mode':
                strategy = impute_params.get('strategy', 'mean')  # Default to 'mean' if not provided
                if strategy == 'most':  # Handle the case where the frontend sends 'most' for "Most Frequent"
                    strategy = 'most_frequent'
                imputer = SimpleImputer(strategy=strategy)
                df[columns] = imputer.fit_transform(df[columns])

            elif impute_choice == 'knn':
                n_neighbors = int(impute_params.get('n_neighbors', 5))
                metric = 'nan_euclidean'  # Enforce using 'nan_euclidean' only
                imputer = KNNImputer(n_neighbors=n_neighbors, metric=metric)
                df[columns] = imputer.fit_transform(df[columns])

            elif impute_choice == 'mice':
                max_iter = int(impute_params.get('max_iter', 10))
                method = impute_params.get('method', 'pmm')
                estimator = LinearRegression() if method == 'regression' else None
                imputer = IterativeImputer(max_iter=max_iter, estimator=estimator, random_state=42)
                df[columns] = imputer.fit_transform(df[columns])

            elif impute_choice == 'regression':
                model_type = impute_params.get('model', 'linear')
                predictors = impute_params.get('predictors', [])
                for col in columns:
                    df_non_missing = df.dropna(subset=predictors + [col])
                if df_non_missing.empty:
                    return jsonify({"error": f"No valid data to fit the model for column '{col}'"}), 400
                X_train = df_non_missing[predictors]
                y_train = df_non_missing[col]
                model = HistGradientBoostingRegressor()
                model.fit(X_train, y_train)
                missing_rows = df[col].isnull()
                if missing_rows.any():
                    df.loc[missing_rows, col] = model.predict(df.loc[missing_rows, predictors])
            elif impute_choice == 'probability':
                distribution = impute_params.get('distribution')
                params = impute_params.get('parameters', [])

                for col in columns:
                    if distribution == 'normal':
                        if len(params) == 2:  # Check for two parameters: mean and std
                            mean, std = map(float, params)
                            df[col].fillna(np.random.normal(mean, std, df[col].isnull().sum()), inplace=True)
                        else:
                            return jsonify({"error": "Invalid parameters for normal distribution. Expected [mean, std]."}), 400
                    elif distribution == 'uniform':
                        if len(params) == 2:  # Check for two parameters: low and high
                            low, high = map(float, params)
                            df[col].fillna(np.random.uniform(low, high, df[col].isnull().sum()), inplace=True)
                        else:
                            return jsonify({"error": "Invalid parameters for uniform distribution. Expected [low, high]."}), 400
                    else:
                        return jsonify({"error": "Invalid distribution type. Expected 'normal' or 'uniform'."}), 400
                    
            elif impute_choice == 'autoencoder':
                hidden_layers = int(impute_params.get('hidden_layers', 2))
                activation = impute_params.get('activation', 'relu')
                epochs = int(impute_params.get('epochs', 50))
                learning_rate = float(impute_params.get('learning_rate', 0.001))

                df_encoded = df[columns].copy()
                df_encoded.fillna(df_encoded.mean(), inplace=True)
                
                model = keras.Sequential([
                    keras.layers.InputLayer(shape=(len(columns),)),
                    keras.layers.Dense(hidden_layers, activation=activation),
                    keras.layers.Dense(len(columns))
                ])
                model.compile(optimizer=keras.optimizers.Adam(learning_rate), loss='mse')
                model.fit(df_encoded, df_encoded, epochs=epochs, verbose=0)
                df[columns] = model.predict(df_encoded)

        df.to_pickle('current_df.pkl')
        missing_stats, missing_percentage, data_types, _, _ = visualize_missing_values(df)
        missing_data_table = generate_missing_data_table(missing_stats, missing_percentage, data_types)
        
        return jsonify({
            "message": "Processing complete",
            "processed": True,
            "missing_stats": missing_stats,
            "missing_percentage": missing_percentage,
            "missing_data_table": missing_data_table
        })
    except Exception as e:
        print(f"Error in process_data: {str(e)}")  # Debugging
        return jsonify({"error": str(e)}), 500
    
    
@mv_bp.route('/data_overview', methods=['GET'])
def data_overview():
    try:
        df = pd.read_pickle('current_df.pkl')
        missing_stats, missing_percentage, data_types, sample_data, missing_values_plot = visualize_missing_values(df)
        missing_data_table = generate_missing_data_table(missing_stats, missing_percentage, data_types)
 
        return jsonify({
            "missing_stats": missing_stats,
            "missing_percentage": missing_percentage,
            "data_types": data_types,
            "sample_data": sample_data,
            "missing_values_plot": missing_values_plot,
            "missing_data_table": missing_data_table  
        })
    except Exception as e:
        print(f"Error generating data overview: {str(e)}")
        return jsonify({"error": f"Error generating data overview: {str(e)}"}), 500


@mv_bp.route('/customize_plot', methods=['POST'])
def customize_plot():
    try:
        df = pd.read_pickle('current_df.pkl')
        color_map = request.json.get('colorMap', 'viridis')
        plot_width = int(request.json.get('plotWidth', 8))
        plot_height = int(request.json.get('plotHeight', 6))
        missing_color = request.json.get('missingColor', '#000000')
        present_color = request.json.get('presentColor', '#FFFFFF')
        print(f"Customization parameters received: color_map={color_map}, plot_width={plot_width}, plot_height={plot_height}, missing_color={missing_color}, present_color={present_color}")
        os.makedirs('static/images', exist_ok=True)
        missing_values_plot = 'missing_values_plot.png'
        save_path = os.path.join('static', 'images', missing_values_plot)
        generate_missing_values_plot(df, save_path, color_map, plot_width, plot_height, missing_color, present_color)
        print(f"Plot saved to: {save_path}")  # Debugging: Log the save path
        return jsonify({"missing_values_plot": f"images/{missing_values_plot}"})
    except Exception as e:
        print(f"Error customizing plot: {str(e)}")
        import traceback
        traceback.print_exc()  # Debugging: Print the full traceback
        return jsonify({"error": f"Error customizing plot: {str(e)}"}), 500
    
    
