import pandas as pd
import numpy as np

def analyze_missing_data(df):
    """
    Analyze missing data and suggest the best imputation methods for each column.
    """
    results = []
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
        if np.issubdtype(dtype, np.number):
            if missing_percentage == 0:
                description["suggested_methods"].append("None")
                description["explanations"].append("Your Data doesn't contain any missing values and is ready for the next steps✅.")
            elif missing_percentage < 5:
                description["suggested_methods"].append("mean")
                description["explanations"].append("Low percentage of missing values; mean imputation is suitable for numerical data.")
                description["suggested_methods"].append("median")
                description["explanations"].append("Low percentage of missing values; median imputation is suitable for skewed data.")
            elif 5 <= missing_percentage <= 30:
                if df.corr()[col].abs().max() > 0.7:  # Check for strong linear relationships
                    description["suggested_methods"].append("regression")
                    description["explanations"].append("Moderate percentage of missing values; regression imputation is suitable for linear relationships.")
                description["suggested_methods"].append("autoencoder")
                description["explanations"].append("Moderate percentage of missing values; autoencoder imputation is suitable for non-linear relationships.")
                description["suggested_methods"].append("knn")
                description["explanations"].append("Moderate percentage of missing values; KNN imputation preserves relationships between features.")
            else:
                description["suggested_methods"].append("drop")
                description["explanations"].append("High percentage of missing values; dropping the column or the values itself if not harmful is recommended.")

        # Categorical Columns
        else:
            if missing_percentage == 0:
                description["suggested_methods"].append("None")
                description["explanations"].append("Your Data doesn't contain any missing values and is ready for the next steps✅.")
            elif missing_percentage < 5:
                description["suggested_methods"].append("mode")
                description["explanations"].append("Low percentage of missing values; mode imputation is suitable for categorical data.")
                description["suggested_methods"].append("most_frequent")
                description["explanations"].append("Low percentage of missing values; most frequent imputation is suitable for high cardinality data.")
            elif 5 <= missing_percentage <= 30:
                description["suggested_methods"].append("probability")
                description["explanations"].append("Moderate percentage of missing values; probability imputation is suitable for known distributions.")
                description["suggested_methods"].append("mice")
                description["explanations"].append("Moderate percentage of missing values; MICE imputation handles complex relationships.")
            else:
                description["suggested_methods"].append("drop")
                description["explanations"].append("High percentage of missing values; dropping the column or the values itself if not harmful is recommended.")

        results.append(description)

    return results