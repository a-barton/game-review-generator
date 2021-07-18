import boto3

def lambda_handler(event, context):
    prompt = event['prompt']
    print(prompt)
    return {'prompt' : prompt}