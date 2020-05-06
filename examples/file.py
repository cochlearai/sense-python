from cochl_sense.file import FileBuilder

import os

api_key = '<Enter-API-Key>'
file_name = 'resources/siren.wav'

_, file_extension = os.path.splitext(file_name)
file_format = file_extension[1:]
file = open(file_name, 'rb')

sense = FileBuilder()\
    .with_reader(file) \
    .with_format(file_format) \
    .with_api_key(api_key) \
    .build()

result = sense.inference()

print(result.detected_events_timing())

