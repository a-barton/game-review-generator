import os
import boto3
import io
#from transformers import pipeline

bucket = os.environ.get('S3_BUCKET', None)
inference_input_key = 'inference_input/prompt.txt'
output_key = 'inference_output/generated.txt'

if bucket:
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket=bucket, Key=inference_input_key)
    prompt = open(io.BytesIO(obj['Body'].read())).read()
else:
    prompt = open('../../game-review-generator/' + inference_input_key).read()

#generator = pipeline('text-generation', model='EleutherAI/gpt-neo-125M', model_kwargs={'max_length':1000})
#output = generator(prompt, do_sample=True, min_length=50, max_length=500)[0]['generated_text']

output = prompt + ' + output test'

if bucket:
    s3_client.put_object(Body=output, Bucket=bucket, Key=output_key)
else:
    open('../../game-review-generator/' + output_key, mode='w').write(output)