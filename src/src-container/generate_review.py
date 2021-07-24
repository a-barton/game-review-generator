import os
import boto3
import io

bucket = os.environ.get('S3_BUCKET', None)
inference_input_key = 'inference_input/prompt.txt'
output_key = 'inference_output/generated.txt'

if bucket:
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket=bucket, Key=inference_input_key)
    prompt = obj['Body'].read().decode('utf-8')
else:
    prompt = open('../../game-review-generator/' + inference_input_key).read()

output = prompt + ' + output test'

if bucket:
    s3_client.put_object(Body=output, Bucket=bucket, Key=output_key)
else:
    open('../../game-review-generator/' + output_key, mode='w').write(output)