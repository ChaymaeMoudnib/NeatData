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
from flask import Flask, request, jsonify





UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

plt.switch_backend('Agg')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').lower()

    responses = {
        "what can you do?": "I can explain data science concepts, give tips on data cleaning, and recommend visualization techniques.",
        "how to remove missing values?": "You can remove missing values by dropping rows or columns, or by imputing values using mean, median, or KNN imputation.",
        "tell me more about knn imputer": "KNN imputer replaces missing values by considering the nearest neighbors of a data point. It's particularly useful for continuous variables.",
    }

    reply = responses.get(user_message, "I'm not sure about that. Could you rephrase your question or ask about data cleaning or visualization?")

    return jsonify({"reply": reply})


if not os.path.exists('static'):
    os.makedirs('static')