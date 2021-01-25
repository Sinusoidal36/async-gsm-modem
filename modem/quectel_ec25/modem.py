from ..base.modem import ATModem
from ..base.command import Command, ExtendedCommand
from ..base.pdu import encodeSmsSubmitPdu, encodeGsm7
from .response_mapper import ResponseMapper
from .sms import SMS
from .constants import STATUS_MAP, DELETE_FLAG, UNSOLICITED_RESULT_CODES
from typing import List, Type

class ProductInfo:

    def __init__(self, manufacturer, model, revision):
        self.manufacturer = manufacturer
        self.model = model
        self.revision = revision

    def __str__(self):
        return f'{self.manufacturer} {self.model} {self.revision}'

    def to_dict(self):
        return vars(self)

class Modem(ATModem):

    def __init__(self, device:str, baud_rate: int):
        super().__init__(device, baud_rate, UNSOLICITED_RESULT_CODES)

    async def initialize(self):
        await self.ping()

    async def ping(self):
        await self.send_command(Command(b'AT'))

    async def product_info(self) -> Type[ProductInfo]:
        responses = await self.send_command(Command(b'ATI'))
        return ProductInfo(*[r.response.decode() for r in responses[1:4]])

    async def imei(self):
        responses = await self.send_command(Command(b'AT+GSN'))
        return bytes(responses[1]).decode()

    async def read_message(self, index: int) -> Type[SMS]:
        command = ExtendedCommand(b'AT+CMGR').write(str(index).encode())
        responses = await self.send_command(command)
        if b'+CMGR' not in bytes(responses[1]):
            self.logger.debug(f'Message does not exist at index {index}')
            return None
        status, alpha, length = bytes(responses[1]).lstrip(b'+CMGR: ').split(b',')

        return SMS(index, status, alpha, length, bytes(responses[2]))

    async def send_message(self, to_number: str, text: str, timeout: int = 5):
        pdus = encodeSmsSubmitPdu(to_number, text)
        responses = []
        await self.lock()
        for pdu in pdus:
            length = str(pdu[1]).encode()
            command = ExtendedCommand(b'AT+CMGS').write(length)
            await self.write(command)
            await self.read(terminator=bytes(command)) # read out and discard command echo
            await self.read(seperator=b'> ', terminator=b'') # read out and discard prompt
            command = ExtendedCommand(pdu[0].hex().upper().encode()).execute()
            await self.write(command, terminator=chr(26).encode()) # send pdu with CTRL-Z terminator
            responses += await self.read(timeout=timeout)
        self.unlock()
        return responses

    async def list_messages(self, status: str = 'ALL') -> List[SMS]:
        assert status in STATUS_MAP, \
            KeyError(f'Invalid status {status}: {tuple(STATUS_MAP.keys())}')
        status = STATUS_MAP[status]

        command = ExtendedCommand(b'AT+CMGL').write(status)
        responses = await self.send_command(command)
        responses = responses[1:-2]

        messages = []
        for n in range(len(responses)//2):
            index, status, alpha, length = bytes(responses[n*2]).lstrip(b'+CMGL: ').split(b',')
            pdu = bytes(responses[(n*2)+1])
            messages.append(SMS(index, status, alpha, length, pdu))

        return messages

    async def delete_message(self, index: int):
        command = ExtendedCommand(b'AT+CMGD').write(str(index).encode())
        await self.send_command(command)
        self.logger.debug(f'Deleted message at index {index}')

    async def delete_messages(self, del_flag: str = 'ALL'):
        assert del_flag in DELETE_FLAG, \
            KeyError(f'Invalid delete flag {del_flag}: {tuple(DELETE_FLAG.keys())}')

        command = ExtendedCommand(b'AT+CMGD').write(b'0', DELETE_FLAG[del_flag])
        await self.send_command(command)
        self.logger.debug(f'Deleted {del_flag} messages')