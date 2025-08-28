import os
import tempfile
import cloudpickle
from google.cloud import storage
from src.config import Config

MODEL_CACHE = {}

def load_model_from_gcp(model_name: str):
    if model_name in MODEL_CACHE:
        return MODEL_CACHE[model_name]

    client = storage.Client()
    bucket = client.bucket(Config.GS_BUCKET_NAME)
    blob = bucket.blob(model_name)

    # Use system temp dir (works on Windows, Linux, Cloud Run)
    tmp_dir = tempfile.gettempdir()
    local_path = os.path.join(tmp_dir, model_name.split("/")[-1])

    blob.download_to_filename(local_path)

    with open(local_path, "rb") as f:
        model = cloudpickle.load(f)

    MODEL_CACHE[model_name] = model
    return model
