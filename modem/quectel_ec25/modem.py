from ..base import ATModem, Command, ExtendedCommand
from .response_mapper import ResponseMapper
from .sms import SMSStatus, SMS
from .constants import STATUS_MAP, DELETE_FLAG
from typing import List, Type

class ProductInfo:

    def __init__(self, manufacturer, model, revision):
        self.manufacturer = manufacturer
        self.model = model
        self.revision = revision

    def __str__(self):
        return f'{self.manufacturer} {self.model} {self.revision}'

    def to_dict(self):
        return {
            'manufacturer': self.manufacturer,
            'model': self.model,
            'revision': self.revision
        }

class Modem(ATModem):

    def __init__(self, device:str, baud_rate: int):
        super().__init__(device, baud_rate, ResponseMapper())

    async def initialize(self):
        await self.ping()

    async def ping(self):
        command = Command(b'AT', b'OK')
        await self.send_command(command)

    async def product_info(self) -> Type[ProductInfo]:
        command = ExtendedCommand(b'ATI', b'OK').execute()
        responses = await self.send_command(command)
        return ProductInfo(*[r.response.decode() for r in responses[:3]])

    async def read_message(self, index: int) -> Type[SMS]:
        command = ExtendedCommand(b'AT+CMGR', b'OK').write(str(index).encode())
        responses = await self.send_command(command)

    async def list_messages(self, status: str = 'ALL') -> List[SMSStatus]:
        assert status in STATUS_MAP, \
            KeyError(f'Invalid status {status}: {tuple(STATUS_MAP.keys())}')
        status = STATUS_MAP[status]

        command = ExtendedCommand(b'AT+CMGL', b'OK').write(status)
        responses = await self.send_command(command)

        statuses = []
        for n in range(len(responses)//2):
            index, stat, alpha, length = responses[n*2].response.lstrip(b'+CMGL: ').split(b',')
            pdu = responses[(n*2)+1].response
            statuses.append(SMSStatus(index, stat, alpha, length, pdu))

        return statuses

    async def delete_message(self, index: int):
        command = ExtendedCommand(b'AT+CMGD', b'OK').write(str(index).encode())
        await self.send_command(command)
        self.logger.debug(f'Deleted message at index {index}')

    async def delete_messages(self, del_flag: str = 'ALL'):
        assert del_flag in DELETE_FLAG, \
            KeyError(f'Invalid delete flag {del_flag}: {tuple(DELETE_FLAG.keys())}')

        command = ExtendedCommand(b'AT+CMGD', b'OK').write(b'0', DELETE_FLAG[del_flag])
        await self.send_command(command)
        self.logger.debug(f'Deleted {del_flag} messages')