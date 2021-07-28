import os
import boto3
import pandas as pd

from utils import ReviewModel
from utils import LOGGER

# Determine what conditions container is running in (based on env variables)
bucket = os.environ.get("S3_BUCKET", None)
location = "aws" if bucket else "local"
mode = os.environ.get("MODE", None)

if location == "local":
    os.chdir('artifacts/')

if mode == "train":
    LOGGER.info("Commencing Model Fine Tuning")
    training_input_key = "training_input/data.csv"
    model_artifacts_key = "fine-tuned-model"
    model = ReviewModel(location=location)
    model.fine_tune(
        data_path=training_input_key, 
        model_save_path=model_artifacts_key
    )
    LOGGER.info("Model Fine Tuning Complete")
else:
    LOGGER.info("Commencing Model Inference")
    inference_input_key = "inference_input/prompt.txt"
    inference_output_key = 'inference_output/generated.txt'
    model_checkpoint = "fine-tuned-model"
    model = ReviewModel(location=location, model_checkpoint=model_checkpoint)
    model.predict(
        prompt_input_path=inference_input_key, 
        prompt_output_path=inference_output_key, 
        max_length=300
    )
    LOGGER.info("Model Inference Complete")