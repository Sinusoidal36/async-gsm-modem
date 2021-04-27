from .response import Response

class CommandError(Exception):
    """Raised when a command returns an error response
    
    Attributes:
        error -- The received error
    """
    
    def __init__(self, error: bytes = None, msg: str = "Modem returned error response"):
        self.error = error
        self.msg = msg
        super().__init__(self.msg)

class CommandFailed(Exception):
    """Raised when a command fails"""
    pass

class ModemConnectionError(Exception):
    """Raised when modem is unresponsive"""
    pass