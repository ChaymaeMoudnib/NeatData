import os
from flask import Flask, render_template, jsonify, Response,send_from_directory,send_file
from features.feature import feature_bp  
from features.sampling import sampling_bp
from features.dimension import dimension_bp
from features.save import save_bp
from features.mv import mv_bp
from features.encode import encode_bp
from features.upload import upload_bp
from features.test import db_bp
from features.visualise import visualise_bp
from features.correcting import correct_bp
from features.smart_imp import smartimp_bp
from features.utils import utile_bp
from features.outliers import outliers_bp
import numpy as np
import pandas as pd
from flask_cors import CORS  
import shutil 




app = Flask(__name__)
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

CORS(app)

if not os.path.exists('static'):
    os.makedirs('static')
if not os.path.exists('uploads'):
    os.makedirs('uploads')

app.config['UPLOAD_FOLDER'] = 'uploads'  

# Register blueprints for different features
app.register_blueprint(upload_bp)
app.register_blueprint(sampling_bp)
app.register_blueprint(feature_bp)
app.register_blueprint(visualise_bp)
app.register_blueprint(dimension_bp)
app.register_blueprint(mv_bp)
app.register_blueprint(encode_bp)
app.register_blueprint(save_bp)
app.register_blueprint(db_bp)
app.register_blueprint(correct_bp)
app.register_blueprint(smartimp_bp)
app.register_blueprint(outliers_bp)
app.register_blueprint(utile_bp)

###missing value report :

@app.route('/reset', methods=['POST'])
def reset_data():
    try:
        empty_df = pd.DataFrame()
        empty_df.to_pickle('current_df.pkl')
        print("DataFrame reset successfully.") 
        static_folder = os.path.join('static', 'images')
        if os.path.exists(static_folder):
            shutil.rmtree(static_folder)  
            print("Deleted static/images folder.")  
        os.makedirs(static_folder)  
        print("Recreated static/images folder.")  # Debug: Confirm folder recreation
        return jsonify({"message": "Data reset successfully."})
    except Exception as e:
        print("Error resetting data:", str(e))  # Debug: Print the full error
        return jsonify({"error": f"Error resetting data: {str(e)}"}), 500
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/correct', methods=['GET'])
def correct():
    return render_template('correcting.html')

@app.route('/Smart_Missing_Values', methods=['GET'])
def smart1():                                                                                                                                                                                                                                                                                  
    return render_template('smart_imputation.html')
    
@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/visualise', methods=['GET'])
def visualise_page():
    return render_template('Visualise.html')

@app.route('/transform', methods=['GET'])
def transform():
    return render_template('transform.html')

@app.route('/missing_values')
def missing_values2():
    return render_template('MV.html')

@app.route('/encoding')
def encoding():
    return render_template('encoding.html')

@app.route('/Feature_engineering')
def dimensionality_reduction():
    return render_template('Dimensionality_reduction.html')

@app.route('/Outliers')
def outliers():
    return render_template('outliers.html')

@app.route('/road')
def road():
    return render_template('road.html')

@app.route('/Characteristics_Selection')
def characteristics_selection():
    return render_template('Characteristics_Selection.html')

@app.route('/Data_Sampling')
def data_sampling():
    return render_template('sampling.html')

@app.route('/static/images/<filename>')
def serve_image(filename):
    """
    Serve static images for the HTML report.
    """
    return send_from_directory(os.path.join('static', 'images'), filename)

@app.route('/DataQuality')
def test():
    return render_template('DataQ.html')

@app.route('/download_plot')
def download_plot():
    return send_from_directory('static/plots', 'missing_values_plot.png', as_attachment=True)

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
