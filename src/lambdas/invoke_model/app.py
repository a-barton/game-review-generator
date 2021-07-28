import boto3

def lambda_handler(event, context):
    prompt = event.get('prompt')
    mode = event.get('mode', 'predict')
    bucket = event.get('bucket')
    inference_input_key = 'inference_input/prompt.txt'

    s3_client = boto3.client('s3')
    s3_client.put_object(Body=prompt, Bucket=bucket, Key=inference_input_key)

    batch_client = boto3.client('batch')

    batch_job = batch_client.submit_job(
        jobName='BatchProcessingJobQueue', 
        jobQueue='BatchProcessingJobQueue', 
        jobDefinition='BatchJobDefinition',
        containerOverrides={
            'environment' : [
                {
                    'name' : 'MODE',
                    'value' : mode
                }
            ]
        }
    )

    return batch_job