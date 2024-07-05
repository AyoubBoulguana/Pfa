import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Load the dataset
data = pd.read_csv("Housing.csv")

# Transform categorical variables into dummy variables
data_transformed = pd.get_dummies(data, columns=['date'])

# Separate the target variable
y = data_transformed["price"]
x = data_transformed.drop(columns=['price'])

# Split the data into training and testing sets
train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.15, random_state=42)

# Initialize and train the Random Forest Regressor model
rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
rf_regressor.fit(train_x, train_y)

def predict(input_data):
    # Ensure input data has the same structure as the training data
    input_df = pd.DataFrame(input_data, index=[0])
    input_df = pd.get_dummies(input_df)
    # Align the input_df to the training set's columns
    input_df = input_df.reindex(columns=x.columns, fill_value=0)
    
    prediction = rf_regressor.predict(input_df)
    return prediction[0]

def get_model_metrics():
    predicted_y = rf_regressor.predict(test_x)
    
    mse = mean_squared_error(test_y, predicted_y)
    r2 = r2_score(test_y, predicted_y)
    accuracy_percentage = r2 * 100

    return {
        "Mean Squared Error": mse,
        "R^2 Score": r2,
        "Accuracy Percentage": accuracy_percentage,
        "Feature Importances": rf_regressor.feature_importances_.tolist()
    }
