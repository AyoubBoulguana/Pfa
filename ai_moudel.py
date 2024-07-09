import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Load the dataset
data = pd.read_csv("Housing.csv")



# Separate the target variable (price) from the features
y = data["price"]
x = data.drop(columns=['price'])

# Split the data into training and testing sets
train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.15, random_state=42)


rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
rf_regressor.fit(train_x, train_y)
predictions = rf_regressor.predict(test_x)
mse = mean_squared_error(test_y, predictions)
r2 = r2_score(test_y, predictions)


with open('model.pkl', 'wb') as model_file:
    pickle.dump(rf_regressor, model_file)

