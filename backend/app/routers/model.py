from fastapi import APIRouter
from app.schemas.model.model_request import PreicePredictionRequest
from app.schemas.model.model_response import PreicePredictionResponse
from app.models.model import predict_price

router = APIRouter(
    tags=["Model"]
)

#Model API
@router.post(
    "/predict",
    response_model=PreicePredictionResponse
)
def predict(data: PreicePredictionRequest):
    features = [
        data.area,
        data.floor,
        data.building_age,
        data.subway_distance
    ]

    result_price = predict_price(features)

    return PreicePredictionResponse(predicted_price=result_price)