import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib  

np.random.seed(42)
dates = pd.date_range(start='2021-01-01', periods=730)  # 2 years of daily data
prices = np.random.normal(loc=100, scale=10, size=len(dates)).cumsum()  # Simulated prices

data = pd.DataFrame({'date': dates, 'close_price': prices})
data['date'] = pd.to_datetime(data['date'])

data['target'] = data['close_price'].shift(-1)  
data = data[:-1] 

X = data['close_price'].values[:-1].reshape(-1, 1)
y = data['target'].values[:-1]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Model trained and saved as 'linear_regression_model.pkl'")
print(f"Mean Squared Error: {mse:.2f}")
print(f"R^2 Score: {r2:.2f}")

joblib.dump(model, 'linear_regression_model.pkl')
