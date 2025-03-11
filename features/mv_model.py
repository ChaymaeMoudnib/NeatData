from flask import Blueprint, render_template
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.colors import LinearSegmentedColormap
from sklearn.preprocessing import LabelEncoder



mvmodel_bp = Blueprint('mvmodel', __name__)
def analyze_missing_data(df):
    """
    Analyze missing data and suggest the best imputation methods for each column.
    """
    results = []
    numerical_columns = df.select_dtypes(include=['number']).columns  # Identify numerical columns

    for col in df.columns:
        missing_percentage = df[col].isnull().mean() * 100
        dtype = df[col].dtype
        description = {
            "column": col,
            "missing_percentage": missing_percentage,
            "dtype": dtype,
            "suggested_methods": [],
            "explanations": []
        }

        # Numerical Columns
        if col in numerical_columns:
            if missing_percentage == 0:
                description["suggested_methods"].append("None")
                description["explanations"].append("Your data doesn't contain missing values and is ready for the next steps✅.")
            elif missing_percentage < 5:
                description["suggested_methods"].extend(["mean", "median"])
                description["explanations"].extend([
                    "Low percentage of missing values; mean imputation is suitable for numerical data.",
                    "Low percentage of missing values; median imputation is suitable for skewed data."
                ])
            elif 5 <= missing_percentage <= 30:
                # Apply correlation-based regression imputation **only to numerical columns**
                if col in df.corr().columns and df.corr()[col].abs().max() > 0.7:
                    description["suggested_methods"].append("regression")
                    description["explanations"].append("Moderate percentage of missing values; regression imputation is suitable for numerical columns with strong correlations.")
                
                description["suggested_methods"].extend(["autoencoder", "knn"])
                description["explanations"].extend([
                    "Moderate percentage of missing values; autoencoder imputation is suitable for non-linear relationships.",
                    "Moderate percentage of missing values; KNN imputation preserves relationships between features."
                ])
            else:
                description["suggested_methods"].append("drop")
                description["explanations"].append("High percentage of missing values; dropping the column or values is recommended if not harmful.")

        # Categorical Columns
        else:
            if missing_percentage == 0:
                description["suggested_methods"].append("None")
                description["explanations"].append("Your data doesn't contain missing values and is ready for the next steps✅.")
            elif missing_percentage < 5:
                description["suggested_methods"].extend(["mode", "most_frequent"])
                description["explanations"].extend([
                    "Low percentage of missing values; mode imputation is suitable for categorical data.",
                    "Low percentage of missing values; most frequent imputation is suitable for high-cardinality data."
                ])
            elif 5 <= missing_percentage <= 30:
                description["suggested_methods"].extend(["probability", "mice"])
                description["explanations"].extend([
                    "Moderate percentage of missing values; probability imputation is suitable for known distributions.",
                    "Moderate percentage of missing values; MICE imputation handles complex relationships."
                ])
            else:
                description["suggested_methods"].append("drop")
                description["explanations"].append("High percentage of missing values; dropping the column or values is recommended if not harmful.")

        results.append(description)

    return results


colors = ["#FFFFFF", "#1e53e6"]  
custom_cmap = LinearSegmentedColormap.from_list("custom", colors)


def visualize_missing_data(df, save_path):
    if not df.empty:
        plt.figure(figsize=(10, 6))
        sns.heatmap(df.isnull(), cbar=False, cmap=custom_cmap)
        plt.title("Missing Data Patterns")
        plt.savefig(save_path)
        plt.close()
        print(f"Missing data heatmap saved at: {save_path}")
    else:
        print("The DataFrame is empty. No heatmap can be generated.")

def visualize_distributions(df, save_folder):
    if df.empty:
        print("The DataFrame is empty. No distribution plots can be generated.")
        return

    numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns

    # Plot distributions for numerical columns
    for col in numerical_cols:
        plt.figure(figsize=(8, 4))
        sns.histplot(df[col].dropna(), kde=True)
        plt.title(f"Distribution of {col}")
        save_path = os.path.join(save_folder, f"{col}_distribution.png")
        plt.savefig(save_path)
        plt.close()
        print(f"Distribution plot for {col} saved at: {save_path}")

def visualize_relationships(df, save_path):
    if df.empty:
        print("The DataFrame is empty. No correlation matrix can be generated.")
        return
    numerical_cols = df.select_dtypes(include=np.number).columns
    if len(numerical_cols) <= 1:
        print("Not enough numerical columns to create a correlation matrix.")
        return
    plt.figure(figsize=(8, 6))
    sns.heatmap(df[numerical_cols].corr(), annot=True, cmap="vlag", center=0, linewidths=0.5, linecolor="white")
    plt.title("Correlation Matrix")
    plt.savefig(save_path)
    plt.close()
    print(f"Correlation matrix saved at: {save_path}")

def visualize_spider_chart(suggestions, save_path):
    if not suggestions:
        print("No suggestions available for the spider chart.")
        return

    labels = ['Missing Percentage', 'Data Type', 'Imputation Methods', 'Explanations']
    num_columns = len(suggestions)
    data = {
        'Missing Percentage': [row['missing_percentage'] for row in suggestions],
        'Data Type': [1 if row['dtype'] == 'object' else 0 for row in suggestions],  # Dummy value for categorical/numerical
        'Imputation Methods': [len(row['suggested_methods']) for row in suggestions],
        'Explanations': [len(row['explanations']) for row in suggestions]
    }

    normalized_data = {}
    for key, values in data.items():
        max_value = max(values) if max(values) > 0 else 1
        normalized_data[key] = np.array(values) / max_value

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]  

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    for i in range(num_columns):
        values = [normalized_data[key][i] for key in labels]
        values += values[:1] 
        ax.plot(angles, values, label=suggestions[i]['column'])
        ax.fill(angles, values, alpha=0.25)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title('Spider Chart: Imputation Criteria for Columns with Missing Values', size=14, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
    plt.savefig(save_path)
    plt.close()
    print(f"Spider chart saved at: {save_path}")




