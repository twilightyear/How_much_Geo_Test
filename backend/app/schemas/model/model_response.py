from pydantic import BaseModel

class PreicePredictionResponse(BaseModel):
    predicted_price: float