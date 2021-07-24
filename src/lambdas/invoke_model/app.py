import boto3

def lambda_handler(event, context):
    prompt = event['prompt']
    bucket = event['bucket']
    inference_input_key = 'inference_input/prompt.txt'

    s3_client = boto3.client('s3')
    s3_client.put_object(Body=prompt, Bucket=bucket, Key=inference_input_key)

    batch_client = boto3.client('batch')

    batch_job = batch_client.submit_job(
        jobName='BatchProcessingJobQueue', 
        jobQueue='BatchProcessingJobQueue', 
        jobDefinition='BatchJobDefinition'
    )

    return batch_job