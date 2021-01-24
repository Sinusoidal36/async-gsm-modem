from .constants import STATUS_MAP_R

class SMSStatus:

    def __init__(
        self,
        index: bytes,
        status: bytes,
        alpha: bytes,
        length: bytes,
        pdu: bytes,
        ):

        self.index = int(index)
        self.status = STATUS_MAP_R[status]
        self.length = int(length)
        self.pdu = pdu
        self.alpha = alpha.decode()

    def __str__(self):
        return f'SMSStatus(index={self.index}, ' \
                f'status={self.status}, ' \
                f'length={self.length}, ' \
                f'alpha={self.alpha})'
    
    def to_dict(self):
        return {
            'index': self.index,
            'status': self.status,
            'length': self.length,
            'alpha': self.alpha,
            'pdu': self.pdu
        }

class SMS:
    pass