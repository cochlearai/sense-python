from .constants import HOST, MAX_DATA_SIZE, SERVER_CA_CERTIFICATE, USER_AGENT, API_VERSION
from .proto import SenseClient_pb2, SenseClient_pb2_grpc
from .result import Result,default_event_filter

import grpc
import warnings
import copy
import threading

MIN_RECOMMANDED_SAMPLING_RATE = 22050

STREAM_FORMAT = {
    "float32": 4,
    "float64": 8,
    "int32": 4,
    "int64": 8
}


class Stream:
    def __init__(self, api_key, streamer, sampling_rate, data_type, host, max_events_history_size):
        self.__api_key = api_key
        self.__streamer = streamer
        self.__sampling_rate = sampling_rate
        self.__data_type = data_type
        self.__host = host
        self.__max_events_history_size = max_events_history_size

        self.__inferenced = False
        self.__buffer = b''
        self.__channel = None

    def close(self):
        if not self.__inferenced:
            raise RuntimeError("canot close stream if this one was not inferenced")
        if self.__channel == None:
            raise RuntimeError("stream was already closed")
        self.__channel.close()
        self.__chanel = None

    def inference(self, callback , filter=default_event_filter):
        thread = threading.Thread(target=self.__inference, args=(callback, filter,))
        thread.start()

    def __inference(self, callback, filter):
        iterator = self.__send_to_grpc()

        initial_resp = iterator.next()

        result = Result(initial_resp.outputs)
        result.set_filter(filter)  
        if len(result.detected_events()) > 0:
            callback(copy.deepcopy(result))

        for resp in iterator:
            new_result = Result(resp.outputs)
            new_result.set_filter(filter)

            result._append_new_result(resp.outputs, self.__max_events_history_size)
            
            if len(new_result.detected_events()) > 0:
                callback(copy.deepcopy(result))

    def __data_type_size(self):
        return STREAM_FORMAT.get(self.__data_type)

    def __grpc_requests(self):
        for data in self.__streamer():
            self.__buffer = self.__buffer + data

            while len(self.__buffer) >= self.__data_type_size() * self.__sampling_rate / 2:
                to_send = self.__buffer[:MAX_DATA_SIZE]
                self.__buffer = self.__buffer[MAX_DATA_SIZE:]
                yield SenseClient_pb2.RequestStream(data=to_send,apikey=self.__api_key,sr=self.__sampling_rate,dtype=self.__data_type, api_version=API_VERSION, user_agent=USER_AGENT)
    
    def __send_to_grpc(self):
        if self.__inferenced:
            raise RuntimeError("stream was already inferenced")
        self.__inferenced = True

        credentials = grpc.ssl_channel_credentials(root_certificates=SERVER_CA_CERTIFICATE)
        self.__channel = grpc.secure_channel(self.__host, credentials)
        stub = SenseClient_pb2_grpc.SenseStub(self.__channel)

        requests = self.__grpc_requests()

        iterator = stub.sense_stream(requests)
        return iterator

class StreamBuilder:
    def __init__(self):
        self.sampling_rate_warning = True
        self.host = HOST
        self.max_events_history_size = 0

    def with_api_key(self, api_key):
        self.api_key = api_key
        return self

    def with_streamer(self, streamer):
        self.streamer = streamer
        return self

    def deactivate_low_sampling_rate_warning(self):
        self.sampling_rate_warning = False
        return self

    def with_max_events_history_size(self, n):
        self.max_events_history_size = n

    def with_sampling_rate(self, sampling_rate):
        if sampling_rate < MIN_RECOMMANDED_SAMPLING_RATE and self.sampling_rate_warning:
            warnings.warn("a sampling rate of at least 22050 is recommanded")
        self.sampling_rate = sampling_rate
        return self
    
    def with_data_type(self, data_type):
        if data_type not in STREAM_FORMAT:
            raise NotImplementedError(data_type + " stream data type is not supported")

        self.data_type = data_type
        return self
    
    def with_host(self, host):
        self.host = host
        return self

    def build(self):
        return Stream(
            api_key=self.api_key,
            streamer=self.streamer,
            sampling_rate=self.sampling_rate,
            data_type=self.data_type,
            host=self.host,
            max_events_history_size=self.max_events_history_size)

