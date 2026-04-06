import pandas as pd
from sklearn.linear_model import LassoCV

def get_important_features(model, df):
    importances = model.feature_importances_
    data = list(zip(df, importances))
    df_importances = pd.DataFrame(data, columns=['Feature', 'Importance'])
    importance_mean = df_importances['Importance'].mean()
    selected_features = df.columns[importances > importance_mean]
    print(importance_mean, selected_features)
    return selected_features

def train_lasso_cv(X, Y):
    model = LassoCV(cv=5)
    model.fit(X, Y)
    # feature_coefficients = model.coef_
    # intercept = model.intercept_
    # print(f"Optimal alpha selected by CV: {model.alpha_}")
    # print(f"Coefficients: {feature_coefficients}")
    # print(f"Intercept: {intercept}")
    return model