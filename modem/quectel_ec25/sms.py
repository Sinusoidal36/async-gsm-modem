from .constants import STATUS_MAP_R
from io import StringIO
from smspdu.fields import SMSDeliver

class SMS:

    def __init__(self, index: bytes, status: bytes, alpha: bytes, length: bytes, pdu: bytes):
        self.index = int(index)
        self.status = STATUS_MAP_R[status]
        self.alpha = alpha.decode()
        self.length = int(length)
        self.pdu = pdu

        data = SMSDeliver.decode(StringIO(pdu.decode()))
        self.data = data

        self.text = data['user_data']['data']
        self.from_number = data['sender']['number']
        self.date = data['scts']

    def __str__(self):
        return f'SMS(index={self.index}, ' \
                f'status={self.status}, ' \
                f'date={self.date.strftime("%Y-%m-%dT%H:%M:%S%Z")}, ' \
                f'text={self.text})' \
    
    def to_dict(self):
        return vars(self)