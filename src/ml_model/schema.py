from pydantic import BaseModel, Field
from typing import Literal


class HeartDiseaseInput(BaseModel):
    Age: int = Field(..., ge=2, le=80, description="Age of the patient")
    Sex: Literal["M", "F"] = Field(..., description="Gender: M/F")
    ChestPainType: Literal["ATA", "NAP", "ASY", "TA"] = Field(..., description="Chest Pain Type")
    RestingBP: int = Field(..., ge=10, le=200, description="Resting Blood Pressure")
    Cholesterol: int = Field(..., ge=0, le=603, description="Cholesterol level")
    FastingBS: int = Field(..., ge=0, le=1, description="Fasting Blood Sugar (0 or 1)")
    RestingECG: Literal["Normal", "ST", "LVH"] = Field(..., description="Resting ECG results")
    MaxHR: int = Field(..., ge=57, le=203, description="Maximum Heart Rate")
    ExerciseAngina: Literal["Y", "N"] = Field(..., description="Exercise Induced Angina")
    Oldpeak: float = Field(..., ge=-2.6, le=6.2, description="Oldpeak value")
    ST_Slope: Literal["Up", "Flat", "Down"] = Field(..., description="ST slope type")


class HeartDiseasePrediction(BaseModel):
    prediction: int
    probability: float
