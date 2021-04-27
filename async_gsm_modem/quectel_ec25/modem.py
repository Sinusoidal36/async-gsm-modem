from ..base.modem import ATModem
from ..base.response import Response
from ..base.command import Command, ExtendedCommand
from ..base.pdu import encodeSmsSubmitPdu, encodeGsm7
from .sms import SMS
from .exceptions import *
from .constants import STATUS_MAP, STATUS_MAP_R, DELETE_FLAG, UNSOLICITED_RESULT_CODES
from typing import List, Type
from .info import ProductInfo
import logging
from io import StringIO
from smspdu.fields import SMSDeliver

class Modem(ATModem):

    def __init__(self, device: str, baud_rate: int):
        super().__init__(device, baud_rate, UNSOLICITED_RESULT_CODES)

        self.logger = logging.getLogger('QuectelEC25Modem')

    async def ping(self):
        response = await self.send_command(Command(b'AT'))
        return response == Response([])

    async def product_info(self) -> ProductInfo:
        response = await self.send_command(Command(b'ATI'))
        response = [r.decode() for r in response]
        return ProductInfo(
            manufacturer=response[0],
            model=response[1],
            revision=response[2].replace('Revision: ', '')
        )

    async def imei(self):
        response = await self.send_command(Command(b'AT+GSN'))
        return response[0].decode()

    async def imsi(self):
        response = await self.send_command(Command(b'AT+CIMI'))
        return response[0].decode()

    async def number(self):
        response = await self.send_command(Command(b'AT+CNUM'))
        response = response[0].decode()
        number = response.split(',')[1].replace('"','')
        return number

    def parse_message(self, index, status, alpha, length, pdu) -> SMS:
        data = SMSDeliver.decode(StringIO(pdu.decode()))

        text = str(data['user_data']['data'])
        from_number = data['sender']['number']
        date = data['scts']

        return SMS(
            index=index,
            status=status,
            alpha=alpha,
            length=length,
            pdu=pdu,
            text=text,
            from_number=from_number,
            date=date
        )
    
    async def read_message(self, index: int) -> SMS:
        try:
            command = ExtendedCommand(b'AT+CMGR').write(str(index).encode())
            response = await self.send_command(command)
        except Exception as e:
            self.logger.error('Failed to read message', exc_info=True)
            raise ReadMessageError from e
        
        if response:
            status, alpha, length = response[0].replace(b'+CMGR: ', b'').split(b',')
            pdu = response[1]

            return self.parse_message(index, status, alpha, length, pdu)
        else:
            return

    async def send_message(self, to_number: str, text: str, timeout: int = 5):
        try:
            pdus = encodeSmsSubmitPdu(to_number, text)
            responses = []
            await self.lock()
            for pdu in pdus:
                length = str(pdu[1]).encode()
                command = ExtendedCommand(b'AT+CMGS').write(length)
                await self.write(command)
                await self.read_response(terminator=bytes(command)) # read out and discard command echo
                await self.read_response(seperator=b'> ', terminator=b'') # read out and discard prompt
                command = ExtendedCommand(pdu[0].hex().upper().encode()).execute()
                await self.write(command, terminator=chr(26).encode()) # send pdu with CTRL-Z terminator
                responses.append(await self.read_response(timeout=timeout))
            self.unlock()
            return responses
        except Exception as e:
            self.logger.error('Failed to send message', exc_info=True)
            raise SendMessageError from e

    async def list_messages(self, status: str = 'ALL') -> List[SMS]:
        if status not in STATUS_MAP:
            raise ValueError(f'Invalid status {status}: {tuple(STATUS_MAP.keys())}')
        status = STATUS_MAP[status]

        try:
            command = ExtendedCommand(b'AT+CMGL').write(status)
            response = await self.send_command(command)
            
            if len(response)%2 > 0:
                raise ValueError(f'Expecting even number of parts in response: {response}')

            messages = []
            for n in range(len(response)//2):
                try:
                    message_info = response[n*2]
                    index, status, alpha, length = message_info.replace(b'+CMGL: ', b'').split(b',')
                    pdu = response[(n*2)+1]
                    message = self.parse_message(index, status, alpha, length, pdu)
                    messages.append(message)
                except:
                    self.logger.error(f'Failed to parse message: {response[(n*2):(n*2)+1]}', exc_info=True)

            return messages
        except Exception as e:
            self.logger.error('Failed to list messages', exc_info=True)
            raise ReadMessageError from e

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