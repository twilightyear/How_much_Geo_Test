from pydantic import BaseModel

class PreicePredictionRequest(BaseModel):
    area: float
    floor: int
    building_age: int
    subway_distance: float