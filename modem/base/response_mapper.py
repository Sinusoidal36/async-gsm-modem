from .response import Response

class ResponseMapper:

    responses = []

    def map(self, response: bytes) -> Response:
        for r in self.responses:
            prefix, response_class = r
            if response.startswith(prefix):
                return response_class(response)
        return Response('', response)