from flask import Blueprint, jsonify, request 
import numpy as np
import pandas as pd
import os

quality_bp = Blueprint('quality', __name__)

# Existing functions...

def missing(df):
    missing_p = (df.isnull().sum() / len(df)) * 100  
    col_with_missing = df.columns[df.isnull().any()].tolist()

    if not col_with_missing:  
        return jsonify({
            "message": "No missing values detected in any column.",
            "Max_Missing_Column": None,
            "Max_Missing_Percentage": 0,
            "MV_SCORE": 20
        })
    
    max_missing_col = max(col_with_missing, key=lambda col: missing_p[col])
    max_missing_val = missing_p[max_missing_col]
    
    if max_missing_val >= 30:
        mv_score = 0
    elif max_missing_val >= 15:
        mv_score = 5
    elif max_missing_val >= 5:
        mv_score = 10
    elif max_missing_val >= 1:
        mv_score = 15
    else:
        mv_score = 20  
    
    return jsonify({
        "message": f"Column '{max_missing_col}' has the highest missing percentage.",
        "Max_Missing_Column": max_missing_col,
        "Max_Missing_Percentage": max_missing_val,
        "MV_SCORE": mv_score
    })

def duplicate(df):
    total_rows = len(df)
    unique_rows = len(df.drop_duplicates())
    dup_rows = total_rows - unique_rows
    dup_percentage = (dup_rows / total_rows) * 100 if total_rows > 0 else 0
    
    if dup_percentage >= 15:
        dp_score = 0
    elif dup_percentage >= 10:
        dp_score = 5
    elif dup_percentage >= 1:
        dp_score = 7.5
    else:
        dp_score = 10  
    
    return jsonify({
        "Total_Rows": total_rows,
        "Duplicate_Percentage": round(dup_percentage, 2),
        "dp_score": dp_score
    })

def detect_outliers(df):
    outlier_cols = []
    
    for col in df.select_dtypes(include=['number']).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        if ((df[col] < lower_bound) | (df[col] > upper_bound)).any():
            outlier_cols.append(col)

    outlier_score = 0 if outlier_cols else 10

    return jsonify({
        "Columns_With_Outliers": outlier_cols,
        "Outlier_Score": outlier_score
    })

def formatting(df):
    formatting_issues = {}
    for col in df.columns:
        if df[col].dtype == 'object':
            if df[col].str.contains(r'[^a-zA-Z0-9\s]', regex=True).any():
                formatting_issues[col] = "Contains special characters"
    
    format_score = 10 if not formatting_issues else 0
    
    return jsonify({
        "Formatting_Issues": formatting_issues,
        "Formatting_Score": format_score
    })

def encoding_check(df):
    unencoded_cats = []
    
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() > 4:  # Check for categorical variables with more than four unique values
            unencoded_cats.append(col)
    
    encoding_score = 10 if not unencoded_cats else 0  
    
    return jsonify({
        "Unencoded_Categorical_Variables": unencoded_cats,
        "Encoding_Score": encoding_score
    })

def data_type_validity(df):
    expected_types = {
        'age': 'int64',
        'salary': 'float64',
    }
    
    invalid_cols = []
    for col, expected_type in expected_types.items():
        if col in df.columns and str(df[col].dtype) != expected_type:
            invalid_cols.append(col)
    
    validity_score = 0 if invalid_cols else 10
    
    return jsonify({
        "Invalid_Columns": invalid_cols,
        "Validity_Score": validity_score
    })

def cardinality(df):
    cardinality_score = 10
    high_cardinality_cols = []
    
    for col in df.select_dtypes(include=['object']).columns:
        unique_values = df[col].nunique()
        total_values = len(df[col])
        if unique_values / total_values > 0.5:  
            high_cardinality_cols.append(col)
            cardinality_score = 5  
    
    return jsonify({
        "High_Cardinality_Columns": high_cardinality_cols,
        "Cardinality_Score": cardinality_score
    })

def balance(df, target_col=None):
    if target_col is None or target_col not in df.columns:
        return 0

    class_counts = df[target_col].value_counts(normalize=True)
    if len(class_counts) < 4:
        return 0

    max_proportion = class_counts.max()
    if max_proportion > 0.8:
        return 0
    elif max_proportion > 0.6:
        return 2
    elif max_proportion > 0.4:
        return 4
    else:
        return 5

def correlation(df):
    correlation_matrix = df.corr()
    redundant_features = set()
    threshold = 0.8  

    for col in correlation_matrix.columns:
        high_correlation_cols = correlation_matrix.index[correlation_matrix[col] > threshold].tolist()
        high_correlation_cols.remove(col)  
        redundant_features.update(high_correlation_cols)
        
    num_redundant = len(redundant_features)
    if num_redundant == 0:
        return 10  
    elif num_redundant <= 2:
        return 8  
    elif num_redundant <= 5:
        return 5  
    else:
        return 0  

def domain_specific_checks(df):
    domain_issues = {}
    if 'age' in df.columns:
        out_of_bounds = df[(df['age'] < 0) | (df['age'] > 120)]
        if not out_of_bounds.empty:
            domain_issues['age'] = "Contains out-of-bound values"
    if 'income' in df.columns:
        if df['income'].isnull().any():
            domain_issues['income'] = "Contains missing values"
    if 'gender' in df.columns:
        valid_genders = ['Male', 'Female', 'Other']
        invalid_genders = df[~df['gender'].isin(valid_genders)]
        if not invalid_genders.empty:
            domain_issues['gender'] = "Contains invalid gender entries"
    
    return 5 if not domain_issues else 0

DATA_FILE = "current_df.pkl"

def load_dataframe():
    if not os.path.exists(DATA_FILE):
        return None, {"error": f"File '{DATA_FILE}' not found."}, 404
    df = pd.read_pickle(DATA_FILE)
    if df.empty:
        return None, {"error": "Loaded DataFrame is empty."}, 400
    return df, None, None

@quality_bp.route("/data_quality", methods=["POST"])
def evaluate_data_quality():
    df = pd.read_pickle(DATA_FILE)
    request_data = request.json
    include_balance = request_data.get("include_balance", True)
    include_domain = request_data.get("include_domain", True)
    target_col = request_data.get("target_col", None)
    
    missing_results = missing(df)
    duplicate_results = duplicate(df)
    outlier_results = detect_outliers(df)
    formatting_results = formatting(df)
    validity_results = data_type_validity(df)
    cardinality_results = cardinality(df)
    encoding_results = encoding_check(df)
    
    balance_score = 0
    if include_balance:
        balance_score = balance(df, target_col=target_col)
    
    domain_score = 0
    if include_domain:
        domain_score = domain_specific_checks(df)

    correlation_score = correlation(df)
    
    scores = {
        "MV_SCORE": missing_results.get_json().get("MV_SCORE", 0),
        "DP_SCORE": duplicate_results.get_json().get("dp_score", 0),
        "OUTLIER_SCORE": outlier_results.get_json().get("Outlier_Score", 0),
        "FORMAT_SCORE": formatting_results.get_json().get("Formatting_Score", 0),
        "VALIDITY_SCORE": validity_results.get_json().get("Validity_Score", 0),
        "CARDINALITY_SCORE": cardinality_results.get_json().get("Cardinality_Score", 0),
        "ENCODING_SCORE": encoding_results.get_json().get("Encoding_Score", 0),
        "BALANCE_SCORE": balance_score,
        "DOMAIN_SCORE": domain_score,
        "CORRELATION_SCORE": correlation_score
    }

    # Calculate the total score
    max_feature_score = max(scores.values())
    total_score = 100 - max_feature_score if include_balance or include_domain else 100 - max_feature_score

    # Prepare final response with detailed scores and total score
    final_results = {
        "Missing Results": missing_results.get_json(),
        "Duplicate Results": duplicate_results.get_json(),
        "Outlier Results": outlier_results.get_json(),
        "Formatting Results": formatting_results.get_json(),
        "Validity Results": validity_results.get_json(),
        "Cardinality Results": cardinality_results.get_json(),
        "Encoding Results": encoding_results.get_json(),
        "Balance Score": balance_score,
        "Domain Score": domain_score,
        "Correlation Score": correlation_score,
        "Total Score": total_score,
        "Detailed Scores": scores
    }
    
    return jsonify(final_results)
