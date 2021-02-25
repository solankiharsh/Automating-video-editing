import boto3

# Connect to Amazon Rekognition
client = boto3.client('rekognition', region_name = 'us-east-1')

# Retrieve the face search results
person_to_find = 'dolly'
timestamps=[]

search = client.get_face_search(JobId='361e8f24f5fa682af4d0fce14ce8e5b58d36053f736e5d21d3b2592b21918603', SortBy='INDEX')

while (True):
  for person in search['Persons']:
    try:
      for face_matches in person['FaceMatches']:
        if face_matches['Face']['ExternalImageId'] == person_to_find:
          timestamps.append(person['Timestamp'])
    except KeyError:
      pass

  # Retrieve the next set of results
  try:
    next_token = search['NextToken']
    search = client.get_face_search(JobId='361e8f24f5fa682af4d0fce14ce8e5b58d36053f736e5d21d3b2592b21918603', SortBy='INDEX', NextToken = search['NextToken'])
  except KeyError:
    break

'''
The timestamps array now looks like:
[142080, 142600, 144080, 144600, 153600, 154080, 154600, 155080, 155600, 156080, 346440, 346920, 347440, 347920, 365960, 366440, 369960, 370440]
'''
print(timestamps)
# Break into scenes with start & end times
scenes=[]
start = 0

for timestamp in timestamps:
  if start == 0:
    # First timestamp
    start = end = timestamp
  else:
    # More than 1 second between timestamps? Then scene has ended
    if timestamp - end > 1000:
      # If the scene is at least 1 second long, record it
      if end - start >= 1000:
        scenes.append((start, end))
      # Start a new scene
      start = 0
    else:
      # Extend scene to current timestamp
      end = timestamp
print(scenes)
# Append final scene if it is at least 1 second long
if (start != 0) and (end - start >= 1000):
    scenes.append((start, end))

'''
The scenes array now looks like:
[(99800, 101480), (127520, 131760), ...]
'''

# Convert into format required by Amazon Elastic Transcoder
inputs=[]
for scene in scenes:
  start, end = scene
  inputs.append({
    'Key': 'highlight.mp4',
    'TimeSpan': {
      'StartTime': str(start/1000.),
      'Duration': str((end-start)/1000.)
    }
  })
print(inputs)
'''
The inputs array now looks like:
[
  {'Key': 'trainers.mp4', 'TimeSpan': {'StartTime': '99.8', 'Duration': '1.68'}},
  {'Key': 'trainers.mp4', 'TimeSpan': {'StartTime': '127.52', 'Duration': '4.24'}},
  ...
]
'''

## Call Amazon Elastic Transcoder to stitch together a new video
client = boto3.client('elastictranscoder', region_name = 'us-east-1')
hls_64k_audio_preset_id = '1351620000001-000010'

job = client.create_job(
  PipelineId = '1614182744138-c3b3fm',
  Inputs=inputs,
  Output={'Key': person_to_find + '.mp4', 'PresetId': hls_64k_audio_preset_id}
)

print("Trancoding new video completed")
