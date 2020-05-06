from .constants import MAX_DATA_SIZE, HOST, SERVER_CA_CERTIFICATE, API_VERSION, USER_AGENT
from .proto import SenseClient_pb2, SenseClient_pb2_grpc
from .result import Result

import grpc

FILE_FORMAT= ["mp3","wav","ogg","flac","mp4"]


class File:
    def __init__(self, api_key, reader, format, host):
        self.__inferenced = False
        self.__api_key = api_key
        self.__reader = reader
        self.__format = format
        self.__host = host

    def __grpc_requests(self):
        while True:
            chunk = self.__reader.read(MAX_DATA_SIZE)
            if len(chunk) == 0:
                return
            yield SenseClient_pb2.Request(data=chunk,apikey=self.__api_key,format=self.__format, api_version=API_VERSION, user_agent=USER_AGENT)

    def inference(self):
        if self.__inferenced:
            raise RuntimeError("file was already inferenced")
        self.__inferenced = True

        credentials = grpc.ssl_channel_credentials(root_certificates=SERVER_CA_CERTIFICATE)
        channel = grpc.secure_channel(self.__host, credentials)
        stub = SenseClient_pb2_grpc.SenseStub(channel)

        requests = self.__grpc_requests()
        result =  stub.sense(requests)

        return Result(result.outputs)

class FileBuilder:
    def __init__(self):
        self.host = HOST

    def with_api_key(self, api_key):
        self.api_key = api_key
        return self

    def with_reader(self, reader):
        self.reader = reader
        return self
    
    def with_format(self, format):
        if format not in FILE_FORMAT:
            raise NotImplementedError(format + " format file is not supported")
    
        self.format = format
        return self
    
    def with_host(self, host):
        self.host = host
        return self

    def build(self):
        return File(api_key = self.api_key, 
            reader=self.reader, 
            format=self.format,
            host = self.host)
