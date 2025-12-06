import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle

data = pd.read_csv("StudentsPerformance (1).csv")

X = data.drop(columns=["writing score", "reading score"])
y = data["writing score"]

cat_cols = X.select_dtypes(include='object').columns
le_dict = {}
for col in cat_cols:
    le = LabelEncoder()
    X[col] = le.fit_transform(X[col])
    le_dict[col] = le

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor()
model.fit(X_train, y_train)

score = model.score(X_test, y_test)
print("Model R2 Score:", score)

with open("StudentsPerformance (1).pkl", "wb") as f:
    pickle.dump((model, le_dict), f)

print("Model saved successfully!")