import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_corr_matrix(df): # df must be num cols only
    corr_matrix = df.corr(numeric_only=True)
    plt.figure(figsize=(20, 10))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
    plt.title('Correlation Heatmap (Numeric Features)')
    plt.show()


def plot_corr_hist(df, col, top_index):
    corr = df.corr(numeric_only=True)[col].sort_values(ascending=False)[1:top_index]
    print(corr.index)
    plt.figure(figsize=(8,4))
    corr.plot(kind="bar")
    plt.title(f"Top 10 Features Correlated with {col}")
    plt.ylabel("Correlation")
    plt.show()


def col_hist(df, col):
    # c = 'Electrical'
    # print(df[col].isna().sum())
    # print(df[col].head(100))
    print(df[col].value_counts())
    sns.histplot(df[col])


def plot_grid_hist(df, cols):
    n_cols = 4
    n_rows = int(np.ceil(len(cols) / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
    axes = axes.flatten() 

    for i, col in enumerate(cols):
        sns.histplot(df[col], ax=axes[i], fill=True)
        axes[i].set_title(f'KDE Plot of {col}')

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()


