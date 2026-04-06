import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LinearRegression


class LotFrontageByNeighborhoodImputer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        df = X
        self.global_median_ = df["LotFrontage"].median()
        self.by_neighborhood_ = df.groupby("Neighborhood")["LotFrontage"].median()
        return self

    def transform(self, X):
        X = X.copy()
        lf = X["LotFrontage"]
        missing = lf.isna()

        # map Neighborhood -> median LotFrontage
        neigh_med = X.loc[missing, "Neighborhood"].map(self.by_neighborhood_)
        X.loc[missing, "LotFrontage"] = neigh_med.fillna(self.global_median_)
        return X


class PresenceIndicatorAdder(BaseEstimator, TransformerMixin):
    def __init__(self, cols_to_check):
        self.cols_to_check = cols_to_check

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        for col, newcol in self.cols_to_check.items():
            if col in X.columns:
                X[newcol] = X[col].notna().astype(int)
        return X
    

def log1p_selected(df, skewed_num):
    df = df.copy()
    for c in skewed_num:
        if c in df.columns:
            vals = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
            vals = np.clip(vals, 0.0, None)
            df[c] = np.log1p(vals)
    return df
    

def date_transform(df):
    current_year = 2025
    cols = ['YearBuilt', 'YearRemodAdd', 'GarageYrBlt']
    for col in cols:
        df[col] = current_year - df[col]
    df['TotalMoSold'] = df['MoSold'] + ((current_year - df['YrSold']) * 12)
    return df


def binary_transform(df):
    df['PoolArea'] = (df['PoolArea'] != 0).astype(int)
    return df


def fill_missing(df):
    df['LotFrontage'] = median_imputer.fit_transform(df[['LotFrontage']]).ravel()
    df['MasVnrArea'] = df['MasVnrArea'].fillna(0)
    df['GarageYrBlt'] = median_imputer.fit_transform(df[['GarageYrBlt']]).ravel()
    df.fillna(0, inplace=True)
    return df


def one_hot_encode(df):
    return pd.get_dummies(df, dtype=int, dummy_na=True, drop_first=True)


def scale(df):
    scaled_array = scaler.fit_transform(df)
    return pd.DataFrame(scaled_array, columns=df.columns) 


# Imputer that uses linear regression to input missing values
def linreg_imputer(X, c1, c2):
    model = LinearRegression()
    x_tmp_train = {c1: []}
    y_tmp_train = {c2: []}
    x_tmp_target = {c1: []}
    for _, row in x_df_train.iterrows():
        if not pd.isna(row[c2]):
            x_tmp_train[c1].append(row[c1])
            y_tmp_train[c2].append(row[c2])
        else:
            x_tmp_target[c1].append(row[c1])

        model.fit(pd.DataFrame(x_tmp_train), pd.DataFrame(y_tmp_train))


def drop_columns(df):
    misc = ['MSSubClass', 'MiscVal']
    return df.drop(['MoSold', 'YrSold'], axis=1)
