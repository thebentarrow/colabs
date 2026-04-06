import numpy as np
print(np.__version__)

def get_df_num(X, do_print=False):
    if do_print:
        print("\nNumerical Features:")
    cols = X.select_dtypes(include=[np.number])
    for col in cols.columns.tolist():
        col_type = X[col].dtypes
        unique_count = X[col].nunique()
        if do_print:
            print(f"{col}[{col_type}]: {unique_count}")

    return cols


def get_df_cat(X, do_print=False):
    if do_print:
        print("\nCategorical Features:")
    cols = X.select_dtypes(exclude=[np.number])
    for col in cols.columns.tolist():
        col_type = X[col].dtypes
        unique_count = X[col].nunique()
        if do_print:
            print(f"{col}[{col_type}]: {unique_count}")

    return cols


def get_high_variance_features(df):
    hv_cols = []
    for col in df.columns:
        unique_count = df[col].nunique()
        if unique_count > 15:
            hv_cols.append(col)
    return df[hv_cols].copy()


def get_corr(X, cols):
    print(X[cols].corr()[cols[-1]])


def get_low_variance_features(df):
    for col in df.columns:
        if df[col].nunique() < 20:
            print(col)


def print_variances(df):
    print("High Variance:")
    for col in df.columns:
            unique_count = df[col].nunique()
            if unique_count > 99:
                print(f"{col}: {unique_count}")

    print("\nMedium Variance:")
    for col in df.columns:
            unique_count = df[col].nunique()
            if unique_count > 15 and unique_count < 100:
                print(f"{col}: {unique_count}")

    print("\nLow Variance:")
    for col in df.columns:
            unique_count = df[col].nunique()
            if unique_count < 15:
                print(f"{col}: {unique_count}")


def print_null_cols(df):
    cols_w_nulls = df.columns[df.isna().any()].tolist()
    print(df[cols_w_nulls].isna().sum())

