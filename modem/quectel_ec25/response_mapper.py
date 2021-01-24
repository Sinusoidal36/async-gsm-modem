from ..base import Response, UnsolicitedResponse, ErrorResponse
from ..base import ResponseMapper as ResponseMapperBase

class ResponseMapper(ResponseMapperBase):

    responses = [
        (b'+CMTI', UnsolicitedResponse)
    ]