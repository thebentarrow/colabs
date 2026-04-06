from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

def RFR_grid_search(X, Y):
    param_grid = {
        'n_estimators': [100, 200, 300, 400, 500],
        'max_depth': [None, 10, 20, 30, 40, 50],
        'min_samples_split': [2, 4, 6],
        'min_samples_leaf': [1, 2],
        'bootstrap': [True, False]
    }

    grid_search = GridSearchCV(RandomForestRegressor(), param_grid=param_grid, cv=5)
    grid_search.fit(X, Y)

    print("Best Parameters:", grid_search.best_params_)
    print("Best Estimator:", grid_search.best_estimator_)

def DTR_grid_search(X,Y):
    param_grid = {
        'criterion': ['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
        'max_depth': [10, 15, 20, 30, 40],
        'min_samples_split': [2, 3, 4, 5],
        'min_samples_leaf': [2, 4, 8, 16]
    }
    grid_search = GridSearchCV(DecisionTreeRegressor(), param_grid=param_grid, cv=5)
    grid_search.fit(X, Y)

    print("Best Parameters:", grid_search.best_params_)
    print("Best Estimator:", grid_search.best_estimator_)