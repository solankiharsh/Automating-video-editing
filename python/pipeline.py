import boto3

client = boto3.client('elastictranscoder', region_name='us-east-1')
list_pipelines = client.list_pipelines()

print(list_pipelines)

