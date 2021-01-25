from ..base import Response, UnsolicitedResponse, ErrorResponse

class OKResponse(Response):

    def __init__(self, response: bytes):
        super().__init__('OK', response)

class CMTIResponse(UnsolicitedResponse):
    
    def __init__(self, response: bytes):
        super().__init__('+CMTI', response)
        
        response = response.decode()
        response = response.lstrip('+CMTI: ')
        memory, index = response.split(',')
        memory = memory.strip('"')
        index = int(index)

        self.memory = memory
        self.index = index