from datetime import datetime

class Response:

    def __init__(self, response: bytes):
        self.response = response

    def __str__(self):
        try:
            return f'Response({self.response.decode()})'
        except UnicodeDecodeError:
            return f'Response({self.response})'

    def __bytes__(self):
        return self.response

class UnsolicitedResponse(Response):
    pass

class ErrorResponse(Response):
    pass