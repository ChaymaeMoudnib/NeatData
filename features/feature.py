from flask import Blueprint, jsonify, request
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_selection import SelectKBest, f_classif, chi2, RFE
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier


feature_bp = Blueprint('features', __name__)

@feature_bp.route('/feature_overview', methods=['GET'])
def features_overview():
    try:
        df = pd.read_pickle('current_df.pkl')
        data_types, heatmap_path = visualize_features(df)
        return jsonify({
            "data_types": data_types,
            "heatmap_path": heatmap_path,
            "data": df.fillna('').values.tolist()  # Convert data to list for JSON serialization
        })
    except Exception as e:
        return jsonify({"error": f"Error retrieving data overview: {str(e)}"}), 500

def visualize_features(df):
    data_types = df.dtypes.apply(lambda x: x.name).to_dict()
    heatmap_path = 'heatmap.png'
    generate_heatmap(df, os.path.join('static', heatmap_path))
    return data_types, heatmap_path

def generate_heatmap(df, save_path, colors=['#0000FF', '#FFFFFF', '#FF0000']):
    plt.figure(figsize=(10, 8))
    corr = df.corr()
    sns.heatmap(corr, annot=True, cmap=sns.color_palette(colors))
    plt.savefig(save_path, dpi=100, bbox_inches='tight')
    plt.close()

@feature_bp.route('/customize_heatmap', methods=['POST'])
def customize_heatmap():
    try:
        df = pd.read_pickle('current_df.pkl')
        color1 = request.json.get('color1', '#0000FF')
        color2 = request.json.get('color2', '#FFFFFF')
        color3 = request.json.get('color3', '#FF0000')

        heatmap_path = 'custom_heatmap.png'
        generate_heatmap(df, os.path.join('static', heatmap_path), colors=[color1, color2, color3])
        return jsonify({"heatmap_path": heatmap_path})
    except Exception as e:
        return jsonify({"error": f"Error customizing heatmap: {str(e)}"}), 500 

@feature_bp.route('/select_features', methods=['POST'])
def select_features():
    try:
        choice = request.json.get('choice')
        exclude_columns = request.json.get('excludeColumns', '').split(',')
        num_features = int(request.json.get('numFeatures', 10))
        target_column = request.json.get('target')
        estimator_name = request.json.get('estimator', 'logistic')

        df = pd.read_pickle('current_df.pkl')
        for col in exclude_columns:
            if col.strip() in df.columns:
                df = df.drop(columns=[col.strip()])

        if target_column not in df.columns:
            return jsonify({"error": f"Target column '{target_column}' not found in dataset"}), 400

        X = df.drop(columns=[target_column])
        y = df[target_column]

        selector = get_feature_selector(choice, num_features, estimator_name)
        if selector is None:
            return jsonify({"error": "Invalid choice of feature selection method"}), 400

        X_new = selector.fit_transform(X, y)
        selected_features = X.columns[selector.get_support(indices=True)].tolist()
        selected_df = pd.DataFrame(X_new, columns=selected_features)
        selected_df[target_column] = y.reset_index(drop=True)
        selected_colors = request.json.get('colors', ['#0000FF', '#FFFFFF', '#FF0000'])

        return jsonify({
            "data": selected_df.head().to_dict(orient='list'),
            "columns": selected_features,
            "colors": selected_colors
        })
    except Exception as e:
        return jsonify({"error": f"Error processing data: {str(e)}"}), 500

def get_feature_selector(choice, num_features, estimator_name):
    if choice == 'anova':
        return SelectKBest(f_classif, k=num_features)
    elif choice == 'selectkbest':
        return SelectKBest(k=num_features)
    elif choice == 'chi2':
        return SelectKBest(chi2, k=num_features)
    elif choice == 'rfe':
        estimator = get_estimator(estimator_name)
        if estimator is None:
            return None
        return RFE(estimator, n_features_to_select=num_features)
    return None

def get_estimator(estimator_name):
    if estimator_name == 'logistic':
        return LogisticRegression(solver='liblinear')
    elif estimator_name == 'svm':
        return SVC(kernel='linear')
    elif estimator_name == 'rf':
        return RandomForestClassifier(n_estimators=100)
    return None

@feature_bp.route('/selected_heatmap', methods=['POST'])
def selected_heatmap():
    try:
        columns = request.json.get('columns')
        colors = request.json.get('colors', ['#0000FF', '#FFFFFF', '#FF0000'])
        df = pd.read_pickle('current_df.pkl')
        selected_df = df[columns]

        heatmap_path = 'selected_heatmap.png'
        generate_heatmap(selected_df, os.path.join('static', heatmap_path), colors=colors)
        return jsonify({"heatmap_path": heatmap_path})
    except Exception as e:
        return jsonify({"error": f"Error generating heatmap: {str(e)}"}), 500
