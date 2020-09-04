from . import constants
from .proto import SenseClient_pb2, SenseClient_pb2_grpc
from .result import Result

import grpc

FILE_FORMAT= ["mp3","wav","ogg","flac","mp4"]


class File:
    def __init__(self, api_key, reader, format, host, smartFiltering):
        self.__inferenced = False
        self.__api_key = api_key
        self.__reader = reader
        self.__format = format
        self.__host = host
        self.__smartFiltering = smartFiltering

    def __grpc_requests(self):
        offset = 0
        while True:
            chunk = self.__reader.read(constants.MAX_DATA_SIZE)
            if len(chunk) == 0:
                return
            yield SenseClient_pb2.Audio(data=chunk, segmentOffset=offset, segmentStartTime=0)
            offset += len(chunk)

    def inference(self):
        if self.__inferenced:
            raise RuntimeError("file was already inferenced")
        self.__inferenced = True

        credentials = grpc.ssl_channel_credentials(root_certificates=constants.SERVER_CA_CERTIFICATE)
        channel = grpc.secure_channel(self.__host, credentials)
        stub = SenseClient_pb2_grpc.CochlStub(channel)

        requests = self.__grpc_requests()
 
        metadata = [
            (constants.API_KEY_METADATA, self.__api_key),
            (constants.FORMAT_METADATA, self.__format),
            (constants.API_VERSION_METADATA, constants.API_VERSION),
            (constants.USER_AGENT_METADATA, constants.USER_AGENT),
        ]
        if self.__smartFiltering:
            metadata.append((constants.SMART_FILTERING_METADATA, "true"))

        result =  stub.sensefile(requests, metadata=metadata)


        return Result(result)

class FileBuilder:
    def __init__(self):
        self.host = constants.HOST
        self.smartFiltering = False

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

    def with_smart_filtering(self, smartFiltering):
        self.smartFiltering = smartFiltering
        return self

    def build(self):
        return File(api_key = self.api_key, 
            reader=self.reader, 
            format=self.format,
            host = self.host,
            smartFiltering=self.smartFiltering)
