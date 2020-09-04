import sys
sys.path.append("../")

from cochl_sense.file import FileBuilder

api_key = '< Enter API Key >'
file_name = 'resources/siren.wav'
file_format = 'wav'

file = open(file_name, 'rb')

sense = FileBuilder()\
    .with_api_key(api_key) \
    .with_reader(file) \
    .with_format(file_format) \
    .with_smart_filtering(True) \
    .build()

result = sense.inference()

print(result.detected_events_timing())
