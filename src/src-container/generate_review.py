import os
import json

from utils import ReviewModel
from utils import LOGGER

# Determine what conditions container is running in (based on env variables)
bucket = os.environ.get("S3_BUCKET", None)
location = "aws" if bucket else "local"
mode = os.environ.get("MODE", None)
app_id = os.environ.get("APP_ID", None)

# Load text generation (model inference) hyperparameters from config file
with open("model_inference_hyperparameters.json", mode="r") as f:
    hyperparameters = json.load(f)

if location == "local":
    os.chdir("artifacts/")
    rename = "inference_input/" + str(app_id) + "/"
    LOGGER.debug(os.cwd())
    os.rename("inference_input/<APP_ID>/", rename)

if mode == "train":
    LOGGER.info("Commencing Model Fine Tuning")
    training_input_key = "training_input/data.csv"
    model_artifacts_key = "fine-tuned-model"
    model = ReviewModel(location=location, bucket=bucket)
    model.fine_tune(data_path=training_input_key, model_save_path=model_artifacts_key)
    LOGGER.info("Model Fine Tuning Complete")
else:
    LOGGER.info("Commencing Model Inference")
    inference_input_key = f"inference_input/{app_id}/prompt.txt"
    inference_output_key = f"inference_output/{app_id}/generated.txt"
    model_checkpoint = "fine-tuned-model"
    model = ReviewModel(
        location=location, bucket=bucket, model_checkpoint=model_checkpoint
    )
    model.predict(
        prompt_input_path=inference_input_key,
        prompt_output_path=inference_output_key,
        hyperparameters=hyperparameters,
    )
    LOGGER.info("Model Inference Complete")
