from datetime import datetime

class Response:

    def __init__(self, name: str, response: bytes):
        self.response = response
        self.date = datetime.utcnow()

    def __str__(self):
        return f'Response({self.response.decode()})'

class UnsolicitedResponse(Response):
    pass

class ErrorResponse(Response):
    pass