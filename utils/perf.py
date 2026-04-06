import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def measure(model, predictors, target, do_print=False):
    pred = model.predict(predictors)

    if do_print:
        print(predictors, target, pred)
        
    r2 = r2_score(target, pred)
    rmse = np.sqrt(mean_squared_error(target, pred))
    mae = mean_absolute_error(target, pred)
    mape = np.mean(np.abs(target - pred) / target) * 100

    return pd.DataFrame({
        "R-squared": r2,
        "RMSE": rmse,
        "MAE": mae,
        "MAPE": mape
    }, index=[0])