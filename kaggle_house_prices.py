import numpy as np
import pandas as pd

import torch
import torch.nn as nn
import torch.optim as optim

import xgboost
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def model_performance(model, predictors, target):
    pred = model.predict(predictors)
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

df_train = pd.read_csv('./kaggle/house_prices/train.csv')
df_test = pd.read_csv('./kaggle/house_prices/test.csv')

x_train = df_train.drop(['Id', 'SalePrice'], axis=1)
x_test = df_test.drop(['Id'], axis=1)

# Data Setup
#----------------------------------
## One Hot Encode category features
all_data = pd.concat([x_train, x_test], axis=0)
str_cols = all_data.select_dtypes(include=['str']).columns.tolist()
all_data_encoded = pd.get_dummies(all_data, columns=str_cols, dummy_na=True, drop_first=True)

## Null values
cols_w_nulls = all_data_encoded.columns[all_data_encoded.isnull().any()].tolist()
for col in cols_w_nulls:
    all_data_encoded[col] = all_data_encoded[col].fillna(0)

## Split data
x_train = all_data_encoded[:len(x_train)]
x_test = all_data_encoded[len(x_train):]
y_train = df_train['SalePrice']

# Train models
#----------------------------
m_linreg = LinearRegression()
m_linreg.fit(x_train, y_train)
m_linreg_perf = model_performance(
    m_linreg, x_train, y_train
)
print(m_linreg_perf)

m_rndfrst = RandomForestRegressor(n_estimators=500, max_leaf_nodes=15, n_jobs=-1)
m_rndfrst.fit(x_train, y_train)
m_rndfrst_perf = model_performance(m_rndfrst, x_train, y_train)
print(m_rndfrst_perf)

m_xgb = xgboost.XGBRegressor()
m_xgb.fit(x_train, y_train)
m_xgb_perf = model_performance(m_xgb, x_train, y_train)
print(m_xgb_perf)

x_train[x_train.select_dtypes(include=['bool']).columns] = x_train.select_dtypes(include=['bool']) * 1
x_train_tensor = torch.tensor(x_train.to_numpy(), dtype=torch.float32)
y_train_tensor = torch.tensor(y_train.to_numpy(), dtype=torch.float32).view(-1, 1)

class nn_predict(nn.Module):
    def __init__(self, input_features=287, hidden1=128, hidden2=64, hidden3=32, hidden4=16, output=1, dropout_rate=0.1):
        super().__init__()
        self.fc1 = nn.Linear(input_features, hidden1)
        self.fc2 = nn.Linear(hidden1, hidden2)
        self.fc3 = nn.Linear(hidden2, hidden3)
        self.fc4 = nn.Linear(hidden3, hidden4)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout_rate)
        self.out = nn.Linear(hidden4, output)
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        # x = self.dropout(x)
        
        x = self.fc2(x)
        x = self.relu(x)
        # x = self.dropout(x)

        x = self.fc3(x)
        x = self.relu(x)
        # x = self.dropout(x)

        x = self.fc4(x)
        x = self.relu(x)
        x = self.out(x)
        
        return x
    
m_nn = nn_predict()
loss_function = nn.MSELoss()
optimizer = optim.Adam(m_nn.parameters(), lr=0.01)
epochs = 1000
final_loss = []

for epoch in range(epochs):
    m_nn.train()
    optimizer.zero_grad()
    y_pred = m_nn(x_train_tensor)
    loss = loss_function(y_pred, y_train_tensor)
    loss.backward()
    optimizer.step()
    final_loss.append(loss.item())

    if (epoch+1) % 50 == 0:
        print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item()}")

m_nn.eval()
with torch.no_grad():
    y_pred_test = m_nn(x_train_tensor)
y_pred_test = y_pred_test.numpy()

rmse = np.sqrt(mean_squared_error(y_train, y_pred_test))
r2 = r2_score(y_train, y_pred_test)
print(f'RMSE: {rmse:.2f}')
print(f'R² Score: {r2:.4f}')
 
# Test model
#---------------------------------
results = m_xgb.predict(x_test)

with open('results.csv', 'w') as f:
    print('Id,SalePrice', file=f)
    for i, res in enumerate(results):
        print(f"{df_test.iloc[i]['Id']},{res}", file=f)


