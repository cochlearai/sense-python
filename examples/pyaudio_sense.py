import sys
sys.path.append("../")

from pyaudio import PyAudio, paContinue, paFloat32

import queue
import time

from cochl_sense.stream import StreamBuilder


api_key = '< Enter API Key >'
SECOND_TO_INFERENCE=120


class PyAudioSense:
    def __init__(self):
        self.rate = 22050
        chunk = int(self.rate / 2)
        self.buff = queue.Queue()
        self.audio_interface = PyAudio()
        self.audio_stream = self.audio_interface.open(
             format=paFloat32,
             channels=1, rate=self.rate,
             input=True, frames_per_buffer=chunk,
             stream_callback=self._fill_buffer
        )
        self.total = b''

    def stop(self):
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.buff.put(None)
        self.audio_interface.terminate()
        open("output.raw", "wb").write(self.total)

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self.buff.put(in_data)
        self.total += in_data
        return None, paContinue

    def generator(self):
        while True:
            chunk = self.buff.get()
            if chunk is None:
                return
            yield chunk

stream = PyAudioSense()

sense = StreamBuilder() \
    .with_api_key(api_key) \
    .with_streamer(stream.generator) \
    .with_data_type("float32") \
    .with_sampling_rate(22050) \
    .with_smart_filtering(True) \
    .build() \

def on_detected_events(result):
    print(result.detected_events_timing())

sense.inference(on_detected_events)

print("inferencing")
time.sleep(SECOND_TO_INFERENCE)
stream.stop()
