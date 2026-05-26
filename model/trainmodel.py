import numpy as np
from sklearn.ensemble import RandomForestRegressor
import pickle

# Training data
X = np.array([
    [1, 4.5, 500],
    [2, 4.2, 300],
    [5, 3.8, 100],
    [3, 4.7, 800],
    [10, 4.0, 200]
])

y = np.array([5, 4, 2, 5, 3])

model = RandomForestRegressor()
model.fit(X, y)

# Save model
with open("model/model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model saved successfully!")