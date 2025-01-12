import os
from flask import Flask, request, render_template, jsonify, send_from_directory
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.experimental import enable_iterative_imputer
from sklearn.feature_selection import RFE, SelectKBest, chi2, f_classif
from sklearn.impute import IterativeImputer, KNNImputer, SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.manifold import TSNE
from sklearn.preprocessing import LabelEncoder
import category_encoders as ce
from sklearn.svm import SVC
from flask import Flask, request, jsonify
from flask_cors import CORS  
import openai
import requests


HUGGINGFACE_API_KEY = 'your_huggingface_api_key'  # Get your API key from Hugging Face
MODEL_URL = "https://api-inference.huggingface.co/models/gpt2"  # You can replace with any model


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

plt.switch_backend('Agg')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app)  
def query_huggingface_api(payload):
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
    }
    response = requests.post(MODEL_URL, headers=headers, json=payload)
    return response.json()

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_input = request.json.get('message')

        if not user_input:
            return jsonify({'error': 'No message provided'}), 400

        # Send user input to Hugging Face API
        payload = {
            "inputs": user_input,
        }
        response = query_huggingface_api(payload)

        # Extract and return the model response
        if response.get("error"):
            return jsonify({'error': response['error']}), 500
        else:
            return jsonify({'response': response[0]['generated_text']}), 200

    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500

if not os.path.exists('static'):
    os.makedirs('static')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/missing_values')
def missing_values():
    return render_template('missing_values.html')


@app.route('/missing_values2')
def missing_values2():
    return render_template('MV.html')

@app.route('/encoding')
def encoding():
    return render_template('encoding.html')

@app.route('/Dimensionality_reduction')
def Dimensionality_reduction():
    return render_template('Dimensionality_reduction.html')


@app.route('/road')
def road():
    return render_template('road.html')

@app.route('/Characteristics_Selection')
def Characteristics_Selection():
    return render_template('Characteristics_Selection.html')

@app.route('/Data_Sampling')
def Data_Sampling():
    return render_template('sampling.html')

@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/reset', methods=['POST'])
def reset_data():
    try:
        if os.path.exists('current_df.pkl'):
            os.remove('current_df.pkl')
        return jsonify({ "message": "Data reset successfully."})
    except Exception as e:
        return jsonify({"error": f"Error resetting data: {str(e)}"}), 500
    
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    target_column = request.form.get('target_column')  # Correctly get target column from the form
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        try:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_extension = filename.rsplit('.', 1)[1].lower()
            if file_extension != 'csv':
                df = pd.read_excel(file_path)
                csv_file_path = file_path.rsplit('.', 1)[0] + '.csv'
                df.to_csv(csv_file_path, index=False)
            else:
                csv_file_path = file_path
            df = pd.read_csv(csv_file_path)
            df.to_pickle('current_df.pkl')
            if target_column and target_column not in df.columns:
                return jsonify({"error": f"Target column '{target_column}' not found in dataset"}), 400
            return jsonify({"message": "File uploaded and data loaded successfully."})
        except Exception as e:
            return jsonify({"error": f"File processing failed: {str(e)}"}), 500
    return jsonify({"error": "Only CSV and XLSX files are allowed."}), 400

####

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

@app.route('/sampling_overview', methods=['GET'])
def sampling_overview():
    try:
        if not os.path.exists('current_df.pkl'):
            raise FileNotFoundError('current_df.pkl')
            
        df = pd.read_pickle('current_df.pkl')
        data_types = df.dtypes.apply(lambda x: x.name).to_dict()
        
        missing_values = df.isnull().sum().apply(int).to_dict()
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

@app.route('/sample_data', methods=['POST'])
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

def create_visualizations(sampled_df):
    visualizations = {
        "correlation_matrix": "correlation_matrix.png",
        "pairplot": "pairplot.png"
    }
    sns.pairplot(sampled_df)
    plt.savefig(os.path.join('static', visualizations["pairplot"]))
    plt.close()

    plt.figure(figsize=(10, 8))
    sns.heatmap(sampled_df.corr(), annot=True, cmap='coolwarm')
    plt.savefig(os.path.join('static', visualizations["correlation_matrix"]))
    plt.close()
    return visualizations


#####


@app.route('/Feature_overview', methods=['GET'])
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

@app.route('/customize_heatmap', methods=['POST'])
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
    

    
@app.route('/select_features', methods=['POST'])
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

        if choice == 'anova':
            selector = SelectKBest(f_classif, k=num_features)
        elif choice == 'selectkbest':
            selector = SelectKBest(k=num_features)
        elif choice == 'chi2':
            selector = SelectKBest(chi2, k=num_features)
        elif choice == 'rfe':
            if estimator_name == 'logistic':
                estimator = LogisticRegression(solver='liblinear')
            elif estimator_name == 'svm':
                estimator = SVC(kernel='linear')
            elif estimator_name == 'rf':
                estimator = RandomForestClassifier(n_estimators=100)
            else:
                return jsonify({"error": "Invalid estimator for RFE"}), 400
            selector = RFE(estimator, n_features_to_select=num_features)
        else:
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

@app.route('/selected_heatmap', methods=['POST'])
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

    
#####

def normalize_and_encode(df):
    scaler = StandardScaler()
    return scaler.fit_transform(df)

def apply_dimension_reduction(choice, data):
    if choice == '1':
        model = PCA(n_components=2)
    elif choice == '2':
        model = LinearDiscriminantAnalysis(n_components=2)
    elif choice == '3':
        model = TSNE(n_components=2)
    else:
        raise ValueError("Invalid choice")
    return model.fit_transform(data)

@app.route('/dimension', methods=['POST'])
def dimension():
    try:
        data = request.json.get('data')
        choice = request.json.get('choice')

        # Convert data to DataFrame
        df = pd.DataFrame(data)

        # Ensure all data is numeric
        non_numeric_columns = df.select_dtypes(exclude=[np.number]).columns
        if len(non_numeric_columns) > 0:
            return jsonify({"error": f"Data contains non-numeric values in columns: {', '.join(non_numeric_columns)}"}), 400

        # Check for NaN values
        if df.isnull().values.any():
            nan_columns = df.columns[df.isnull().any()].tolist()
            return jsonify({"error": f"Data contains NaN values in columns: {', '.join(nan_columns)}"}), 400

        # Normalize and reduce the dimension
        normalized_data = normalize_and_encode(df)
        reduced_data = apply_dimension_reduction(choice, normalized_data)

        return jsonify(reduced_data.tolist())
    except Exception as e:
        return jsonify({"error": f"Error processing data: {str(e)}"}), 500

@app.route('/dimension_overview', methods=['GET'])
def dimension_overview():
    try:
        df = pd.read_pickle('current_df.pkl')

        # Debug: Print DataFrame to ensure it contains data
        print(df.head())

        if df.empty:
            return jsonify({"error": "DataFrame is empty"}), 400

        data_types, pairplot_path = visualise_dimension(df)
        return jsonify({
            "data_types": data_types,
            "pairplot_path": pairplot_path,
            "data": df.fillna('').values.tolist()  # Convert data to list for JSON serialization
        })
    except Exception as e:
        return jsonify({"error": f"Error retrieving data overview: {str(e)}"}), 500

def visualise_dimension(df):
    data_types = df.dtypes.apply(lambda x: x.name).to_dict()
    pairplot_path = 'pairplot.png'
    generate_pairplot(df, os.path.join('static', pairplot_path))
    return data_types, pairplot_path

def generate_pairplot(df, save_path):
    if df.empty:
        raise ValueError("DataFrame is empty, cannot generate pairplot")
    sns.pairplot(df)
    plt.savefig(save_path, dpi=100)
    plt.close()

@app.route('/customize_pairplot', methods=['POST'])
def customize_pairplot():
    try:
        df = pd.read_pickle('current_df.pkl')

        # Debug: Print DataFrame to ensure it contains data
        print(df.head())

        if df.empty:
            return jsonify({"error": "DataFrame is empty"}), 400

        plot_color = request.json.get('plotColor', '#FF5733')
        plot_width = int(request.json.get('plotWidth', 6))
        plot_height = int(request.json.get('plotHeight', 4))

        pairplot_path = 'custom_pairplot.png'
        generate_custom_pairplot(df, os.path.join('static', pairplot_path), plot_color, plot_width, plot_height)
        return jsonify({"pairplot_path": pairplot_path})
    except Exception as e:
        return jsonify({"error": f"Error customizing plot: {str(e)}"}), 500

def generate_custom_pairplot(df, save_path, plot_color, plot_width, plot_height):
    if df.empty:
        raise ValueError("DataFrame is empty, cannot generate custom pairplot")
    sns.set(style="ticks")
    plot = sns.pairplot(df, plot_kws={'color': plot_color}, height=plot_height/2, aspect=plot_width/plot_height)

    # Adjust color of histograms
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


#####

def generate_missing_data_table(missing_stats, missing_percentage, data_types):
    table = pd.DataFrame({
        'Column': list(missing_stats.keys()),
        'Missing Values': list(missing_stats.values()),
        'Missing Percentage': list(missing_percentage.values()),
        'Data Type': list(data_types.values())
    })
    return table.to_html(classes='data', header="true", index=False)


@app.route('/data_overview', methods=['GET'])
def data_overview():
    try:
        df = pd.read_pickle('current_df.pkl')
        missing_color = request.args.get('missingColor', '#000000')
        present_color = request.args.get('presentColor', '#FFFFFF')
        missing_stats, missing_percentage, data_types, sample_data, missing_values_plot = visualize_missing_values(df, missing_color, present_color)
        table_html = generate_missing_data_table(missing_stats, missing_percentage, data_types)
        return jsonify({
            "missing_stats": missing_stats,
            "missing_percentage": missing_percentage,
            "data_types": data_types,
            "sample_data": sample_data,
            "missing_values_plot": missing_values_plot,
            "missing_data_table": table_html
        })
    except Exception as e:
        return jsonify({"error": f"Error retrieving data overview: {str(e)}"}), 500

def visualize_missing_values(df, missing_color='#000000', present_color='#FFFFFF'):
    missing_stats = df.isnull().sum().to_dict()
    missing_percentage = (df.isnull().sum() / len(df) * 100).to_dict()
    data_types = df.dtypes.apply(lambda x: x.name).to_dict()
    sample_data = df.head().to_html(classes='data', header="true")
    missing_values_plot = 'missing_values_plot.png'
    generate_missing_values_plot(df, os.path.join('static', missing_values_plot), 'viridis', 8, 6, missing_color, present_color)
    return missing_stats, missing_percentage, data_types, sample_data, missing_values_plot


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


@app.route('/customize_plot', methods=['POST'])
def customize_plot():
    try:
        df = pd.read_pickle('current_df.pkl')
        color_map = request.json.get('colorMap', 'viridis')
        plot_width = int(request.json.get('plotWidth', 8))
        plot_height = int(request.json.get('plotHeight', 6))
        missing_color = request.json.get('missingColor', '#000000')
        present_color = request.json.get('presentColor', '#FFFFFF')
        print(f"Customization parameters received: color_map={color_map}, plot_width={plot_width}, plot_height={plot_height}, missing_color={missing_color}, present_color={present_color}")
        missing_values_plot = 'missing_values_plot.png'
        generate_missing_values_plot(df, os.path.join('static', missing_values_plot), color_map, plot_width, plot_height, missing_color, present_color)
        return jsonify({"missing_values_plot": missing_values_plot})
    except Exception as e:
        print(f"Error customizing plot: {str(e)}")
        return jsonify({"error": f"Error customizing plot: {str(e)}"}), 500


####

@app.route('/encoding_overview', methods=['GET'])
def encoding_overview():
    try:
        df = pd.read_pickle('current_df.pkl')
        data_types, column_categories, sample_data = get_encoding_overview(df)
        return jsonify({
            "data_types": data_types,
            "column_categories": column_categories,
            "sample_data": sample_data
        })
    except Exception as e:
        return jsonify({"error": f"Error retrieving encoding overview: {str(e)}"}), 500

def get_encoding_overview(df):
    data_types = df.dtypes.apply(lambda x: x.name).to_dict()
    column_categories = {col: df[col].unique().tolist() for col in df.select_dtypes(include=['object']).columns}
    sample_data = df.sample(max(15, len(df))).to_html(classes='data', header="true")
    return data_types, column_categories, sample_data






@app.route('/encode', methods=['POST'])
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

    

@app.route('/process', methods=['POST'])
def process_data():
    try:
        df = pd.read_pickle('current_df.pkl')
        choice = request.json.get('choice')
        columns = request.json.get('columns').split(',')
        columns = [col.strip() for col in columns]
        columns_with_missing = df.columns[df.isnull().any()].tolist()

        if 'all' in columns:
            columns = columns_with_missing
        else:
            invalid_columns = [col for col in columns if col not in df.columns]
            if invalid_columns:
                missing_stats, missing_percentage, data_types, sample_data = visualize_missing_values(df)
                return jsonify({
                    "error": f"Invalid columns: {invalid_columns}. Please enter valid column names.",
                    "missing_stats": missing_stats,
                    "missing_percentage": missing_percentage,
                    "data_types": data_types,
                    "sample_data": sample_data
                }), 400

        if choice == '1':
            df = df.dropna(subset=columns)
        elif choice == '2':
            df = df.drop(columns=columns)
        elif choice == '3':
            impute_choice = request.json.get('impute_choice')
            if impute_choice == '1':
                n_neighbors = int(request.json.get('n_neighbors'))
                imputer = KNNImputer(n_neighbors=n_neighbors)
                df = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
            else:
                for col in columns:
                    if impute_choice == '2':
                        imputer = SimpleImputer(strategy='mean')
                    elif impute_choice == '3':
                        imputer = SimpleImputer(strategy='most_frequent')
                    elif impute_choice == '4':
                        imputer = SimpleImputer(strategy='most_frequent')
                    elif impute_choice == '5':
                        if df[col].dtype == object:
                            imputer = SimpleImputer(strategy='most_frequent')
                        else:
                            imputer = SimpleImputer(strategy='mean')
                    elif impute_choice == '6':
                        max_iter = int(request.json.get('max_iter'))
                        imputer = IterativeImputer(max_iter=max_iter)
                    df[col] = imputer.fit_transform(df[[col]]).ravel()

        df.to_pickle('current_df.pkl')
        return jsonify({
            "message": "Data processing complete. Do you want to save the processed data or process other columns?",
            "processed": True
        })
    except Exception as e:
        return jsonify({
            "error": f"Data processing failed. Potential causes: {str(e)}. Ensure that the columns are correctly specified, the data types are appropriate for imputation, and the necessary dependencies are installed."
        }), 500


@app.route('/save', methods=['POST'])
def save():
    try:
        file_format = request.json.get('file_format')
        save_path = request.json.get('save_path')
        filename = request.json.get('filename')

        if not file_format or not save_path or not filename:
            return jsonify({"error": "Missing required information"}), 400

        df = pd.read_pickle('current_df.pkl')

        full_path = os.path.join(save_path, f"{filename}.{file_format}")
        if file_format == 'xlsx':
            df.to_excel(full_path, index=False)
        elif file_format == 'csv':
            df.to_csv(full_path, index=False)
        elif file_format == 'json':
            df.to_json(full_path, orient='records', lines=True)
        elif file_format == 'parquet':
            df.to_parquet(full_path, index=False)
        else:
            return jsonify({"error": "Unsupported file format"}), 400

        return jsonify({"message": f"File saved successfully at {full_path}"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, port=5000)  
