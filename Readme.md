# Sense Python

This repository is split in two folders : 
- `cochl_sense` contains the source code of the cochlear.ai sense python client
- `examples` contains examples sample

## Quick start

Go in `examples` folder

Make sure that dependencies are installed by running `pip install -r requirements.txt`.

You can then inference a file: `python file.py`


If you want to inference a stream, you will need to install `portaudio` on your system.
You can then inference audio from your microphone: `python pyaudio_sense.py`

## Use the library

To use our library, install it by running `pip install cochl-sense`.

You can now import classes:
```python
from cochl_sense.file import FileBuilder
from cochl_sense.stream import StreamBuilder
```

### File

`File` represents a class that can inference audio coming from an audio file.

An audio file is any source of audio data which duration is known at runtime.
Because the duration is known at runtime, the server will wait for the whole file to be received before 
to start inferencing. All inferenced data will be received in one payload.

A file can be, for instance, a mp3 file stored locally, a WAV file accessible from an URL etc...

So far WAV, flac, mp3, ogg, mp4 are supported.

If you are using another file encoding format, let us know at support@cochlear.ai so that we can prioritize it in our internal roadmap.

`File` implements the following interface: 

```python
class File:
    def inference() -> Result: 
```

When calling `inference`, a GRPC connection will be established with the backend, audio data of the file will be sent and a `Result` instance will be returned in case of success (described below).

Note that network is not reached until `inference` method is called.

Note that `inference` can be called only once per `File` instance.

To create a `File` instance, you need to use a `FileBuilder` instance. `FileBuilder` is following the builder pattern and calling its `build` method will create a `File` instance.

`FileBuider` implements the following interface:

```python
class FileBuilder: 
    #api key of cochlear.ai projects available at https://dashboard.cochlear.ai
    def with_api_key(key: str) -> FileBuilder:
    #format of the audio file: can be mp3, flac, WAV, ogg, etc...
    def with_format(format: str) -> FileBuilder:
    #data reader to the file data
    def with_reader(reader) ->FileBuilder:
        #where reader is a type that implements io.BufferedIOBase (see https://docs.python.org/3/library/io.html#io.BufferedIOBase)
    
    #creates a File instance*/
    def build() -> File:
```

Note that `with_api_key`, `with_format` and `with_reader` method needs to be called before calling the `build` method, otherwise an error will be raised.

### Stream

`Stream` represents a class that can inference audio coming from an audio stream.

An audio stream is any source of data which duration is not known at runtime. 
Because the duration is not known, the server will inference audio as it comes. One second of audio will be required before the first result to be returned. After that, one result will be given every 0.5 seconds of audio.

A stream can be, for instance, the audio data coming from a microphone, audio data coming from a web radio, etc...

Streams can be stopped at any moment while inferencing.

For now, the only format that is supported for streaming is a raw data stream (PCM stream). 
Raw data being sent has to be a **mono channel** audio stream. Its sampling rate and data type (int16, int32, float32) has to be given to describe the raw audio data. 

For best performance, we recommand using a sampling rate of 22050Hz and data represented as float32.

Multiple results will be returned by calling a callback function.

If you are using another stream encoding format that is not supported, let us know at support@cochlear.ai so that we can prioritize it in our internal roadmap.

`Stream` implements the following interface: 

```python
class Stream:
    def inference(callback):
        #where callback is a function that takes a Result object defined as below
```

When calling `inference`, a GRPC connection will be established with the backend, audio data of the stream will be sent every 0.5s.
Once the result is returned by the server, the `callback` function is called.

Note that the network is not reached until `inference` method is called.

Note that inference can be called only once per `Stream` instance.

To create a `Stream` instance, you need to use a `StreamBuilder` instance. `StreamBuilder` is following the builder pattern and calling its `build` method will create a `Stream` instance.

`StreamBuider` implements the following interface:

```python
class SrteamBuilder:
    #api key of cochlear.ai projects available at dashboard.cochlear.ai
    def with_api_key(key: str) -> StreamBuilder:
    #type of the pcm stream
    def with_data_type(datatype: str) -> StreamBuilder:
    #sampling rate of the pcm stream
    def with_sampling_rate(samplingRate: int) -> StreamBuilder:
    #data of the pcm stream
    def with_streamer(streamer) -> StreamBuilder:
        #where streamer is a generator of binary string

    #creates a Stream instance*/
    def build() -> Stream:

    #disable sampling rate check
    def deactivate_low_sampling_rate_warning() -> StreamBuilder:
    #max number of events from previous inference to keep in memory
    def with_max_events_history_size(size: number) -> StreamBuilder:
}
```

Note that `with_api_key`, `with_data_type`, `with_sampling_rate`, and `with_streamer` method needs to be called before calling the `build` method, otherwise an error will be thrown.


### Result

Result is a class that is returned by both file and stream when calling `inference` method.

Multiple results will be returned by a stream by calling a callback function. For a file only one result will be returned.

`Result` implements the following interface:
```python
class Result:
    #returns all events
    def all_events() -> List[Event]:
    #returns all events that match the "filter function" defined below
    def detected_events() -> List[Event]:
    #group events that match the "filter function" and shows segments of time of when events were detected
    def detected_events_timing() -> Dictionnary[str, List[Tuple[int, int]]]:
    #return only the "tag" of the event that match the "filter" function
    def detected_tags() -> List[str]:
    #returns the service name: "human-interaction" or "emergency" for instance*/
    def service() -> List[str]:
    #returns a raw json object containing service name and an array of events
    def to_json() -> str:
    #use a filter function: that function takes an event as input and return a boolean. An event will be "detected" if the filter function returns true for that event
    def use_default_filter() -> Result:
        #the default filter is to consider all events as detected. So by default, allEvents() and detectedEvents() will return the same result
    def set_filter(filter): Result
        #where filter is a function that takes an event in input and returns a boolean
```

Note that if you are inferencing a stream, multiple results will be returned. By default, calling `all_events()` will only returned the newly inferenced result.
It's possible to keep track of previous events of the stream. To do so, call the `with_max_events_history_size` method on the `StreamBuilder` class. Its default value is 0,
and increasing it will allow to "remember" previous events. 

### Event

An event contains the following data :

```python
class Event:
    #name of the detected event
    tag: str
    #start timestamp of the detected event since the begining of the inference
    start_time: int
    #end timestamp of the detected event since the begining of the inference
    end_time: int
    #probablity for the event to happen. Its values is between 0 and 1
    probability: str
```
