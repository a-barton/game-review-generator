import json
import click
import subprocess

@click.command()
@click.option("--parameters", required=True)
@click.option("--model_source_bucket", required=True)
def main(parameters, model_source_bucket):
    with open(parameters, "r") as f:
        parameters = json.load(f)

    bucket = parameters["bucket"]
    src = f"s3://{model_source_bucket}/fine-tuned-model"
    dest = f"s3://{bucket}/fine-tuned-model"

    subprocess.check_call(f"aws s3 sync --quiet {src} {dest}".split(" "))
    subprocess.check_call(f"aws s3api put-object --bucket {bucket} --key inference_input/".split(" "))
    subprocess.check_call(f"aws s3api put-object --bucket {bucket} --key inference_output/".split(" "))
    subprocess.check_call(f"aws s3api put-object --bucket {bucket} --key training_input/".split(" "))

    return

if __name__ == "__main__":
    main()