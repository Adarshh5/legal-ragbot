from fastapi import APIRouter, Depends, HTTPException, status
from .schema import HeartDiseaseInput, HeartDiseasePrediction
from .services import HeartDiseaseService, CNNImageService

from src.auth.dependencies import AccessTokenBearer  # your existing JWT dependency


from fastapi import APIRouter, UploadFile, File


ml_router = APIRouter()
access_token_bearer = AccessTokenBearer()

# Service is initialized once, loads model into memory
heart_service = HeartDiseaseService()

@ml_router.post("/predict-heart", 
                response_model=HeartDiseasePrediction, 
                dependencies=[Depends(access_token_bearer)])
async def predict_heart(data: HeartDiseaseInput):
    try:
        return heart_service.predict(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


router = APIRouter()
cnn_service = CNNImageService()

@ml_router.post("/predict-cnn",dependencies=[Depends(access_token_bearer)] )
async def predict_cnn(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = cnn_service.predict(image_bytes)
    return result
