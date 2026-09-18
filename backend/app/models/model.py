import joblib
import numpy as np
import pandas as pd

model_data = joblib.load("app/ml/model.pkl")

model = model_data["model"]
scaler = model_data["scaler"]
FEATURE_NAMES = ["area", "floor", "building_ages", "subway_distance"]

def predict_price(features):

    features_df = pd.DataFrame([features], columns=FEATURE_NAMES)
    features_scaled = scaler.transform(features_df)
    prediction = model.predict(features_scaled)
    
    return float(prediction[0])