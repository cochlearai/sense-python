from pyaudio import PyAudio, paContinue, paFloat32

import queue
import time

from cochl_sense.stream import StreamBuilder, MIN_RECOMMANDED_SAMPLING_RATE

SECOND_TO_INFERENCE=10
api_key = '<Enter-API-Key>'

class PyAudioSense:
    def __init__(self):
        self.rate = MIN_RECOMMANDED_SAMPLING_RATE
        chunk = int(self.rate / 2)
        self.buff = queue.Queue()
        self.audio_interface = PyAudio()
        self.audio_stream = self.audio_interface.open(
             format=paFloat32,
             channels=1, rate=self.rate,
             input=True, frames_per_buffer=chunk,
             stream_callback=self._fill_buffer
        )

    def stop(self):
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.buff.put(None)
        self.audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self.buff.put(in_data)
        return None, paContinue

    def generator(self):
        while True:
            chunk = self.buff.get()
            if chunk is None:
                return
            yield chunk

pa = PyAudioSense()

sense = StreamBuilder() \
    .with_data_type("float32") \
    .with_sampling_rate(MIN_RECOMMANDED_SAMPLING_RATE) \
    .with_streamer(pa.generator) \
    .with_api_key(api_key) \
    .build() \

def on_detected_events(result):
    print(result.detected_events_timing())

sense.inference(on_detected_events)

print("inferencing")
time.sleep(SECOND_TO_INFERENCE)
pa.stop()
