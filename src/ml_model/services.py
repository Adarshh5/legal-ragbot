from typing import Dict
import numpy as np
from .schema import HeartDiseaseInput, HeartDiseasePrediction
from .gcp_handler import load_model_from_gcp
import pandas as pd
import onnxruntime as ort
import numpy as np
from PIL import Image
import io



class HeartDiseaseService:
    MODEL_PATH = "heart_pipeline.cloudpickle"

    def __init__(self):
        self.model = load_model_from_gcp(self.MODEL_PATH)

    def predict(self, data: HeartDiseaseInput) -> HeartDiseasePrediction:
        # Convert input to numpy / dataframe (depending on pipeline)
        df = pd.DataFrame([data.dict()])   # ✅ column names preserved

        # Run prediction
        prediction = self.model.predict(df)[0]

        # Model may require DataFrame or numpy array
        # If pipeline handles preprocessing, direct array works
       
        proba = (
            self.model.predict_proba(df)[0][1]
            if hasattr(self.model, "predict_proba")
            else float(prediction)
        )

        return HeartDiseasePrediction(prediction=int(prediction), probability=float(proba))











import os
import tempfile
import numpy as np
import onnxruntime as ort
from google.cloud import storage
from PIL import Image
import io
from src.config import Config
MODEL_CACHE = {}

class CNNImageService:
    MODEL_NAME = "resnet18_model_EfficientNet_intel_dataset.onnx"
    CLASS_LABELS = ['buildings', 'forest', 'glacier', 'mountain', 'sea', 'street']

    def __init__(self):
        if self.MODEL_NAME in MODEL_CACHE:
            self.session = MODEL_CACHE[self.MODEL_NAME]
        else:
            self.session = self._load_model_from_gcp()
            MODEL_CACHE[self.MODEL_NAME] = self.session

        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def _load_model_from_gcp(self):
        """Download ONNX model from GCS and load into onnxruntime."""
        client = storage.Client()
        bucket = client.bucket(Config.GS_BUCKET_NAME)
        blob = bucket.blob(self.MODEL_NAME)

        tmp_dir = tempfile.gettempdir()
        local_path = os.path.join(tmp_dir, self.MODEL_NAME)

        if not os.path.exists(local_path):
            blob.download_to_filename(local_path)

        session = ort.InferenceSession(local_path, providers=["CPUExecutionProvider"])
        return session

    def preprocess(self, image_bytes: bytes) -> np.ndarray:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((224, 224))

        arr = np.array(img).astype(np.float32) / 255.0
        arr = np.transpose(arr, (2, 0, 1))  # HWC -> CHW
        arr = np.expand_dims(arr, axis=0)   # add batch
        return arr

    def predict(self, image_bytes: bytes):
        arr = self.preprocess(image_bytes)
        outputs = self.session.run([self.output_name], {self.input_name: arr})[0]
        probs = self.softmax(outputs[0])
        pred_class = int(np.argmax(probs))
        pred_label = self.CLASS_LABELS[pred_class]

        return {
            "class_index": pred_class,
            "class_label": pred_label,
            "probabilities": probs.tolist()
        }

    @staticmethod
    def softmax(x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()

