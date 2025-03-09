import os
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-interactive plotting
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

colors = ["#FFFFFF", "#1e53e6"]  # White to Red
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

    numerical_cols = df.select_dtypes(include=np.number).columns
    if len(numerical_cols) == 0:
        print("No numerical columns found in the DataFrame.")
        return

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

    # Normalize data (handle division by zero)
    normalized_data = {}
    for key, values in data.items():
        max_value = max(values) if max(values) > 0 else 1
        normalized_data[key] = np.array(values) / max_value

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]  # Close the loop

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    for i in range(num_columns):
        values = [normalized_data[key][i] for key in labels]
        values += values[:1]  # Close the loop
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