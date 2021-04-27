from .response import Response

class CommandError(Exception):
    """Raised when a command returns an error response
    
    Attributes:
        response -- The received response
    """
    
    def __init__(self, error: bytes, message: str = "Modem returned error response"):
        self.error = error
        self.message = message
        super().__init__(self.message)