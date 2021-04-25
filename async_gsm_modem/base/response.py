from datetime import datetime
from dataclasses import dataclass
from typing import List

@dataclass
class Response:
    chunks: List[bytes]

    def __str__(self):
        try:
            return f'Response({" | ".join([chunk.decode() for chunk in self.chunks])})'
        except UnicodeDecodeError:
            return f'Response({" | ".join([chunk for chunk in self.chunks])})'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.chunks == other

@dataclass
class UnsolicitedResultCode(Response):
    code: bytes

class ErrorResponse(Response):
    pass