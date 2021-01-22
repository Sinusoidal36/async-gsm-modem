import asyncio
from collections import deque
from asyncio.exceptions import IncompleteReadError
from datetime import datetime
import serial_asyncio
from pydantic import BaseModel
from typing import Type
import logging

RESP_TERMINATOR = b'\r\n'
EOL_SEQ = b'\r\n'

class Response:

    def __init__(self, name: str, response: bytes):
        self.name = name
        self.response = response
        self.date = datetime.utcnow()

    def __str__(self):
        return f'Response: {self.name} ({self.response})'

class OKResponse(Response):

    def __init__(self, response: bytes):
        super().__init__('OK', response)

class CMTIResponse(Response):
    
    def __init__(self, response: bytes):
        super().__init__('CMTI', response)
        
        response = response.decode()
        response = response.lstrip('+CMTI: ')
        memory, index = response.split(',')
        memory = memory.strip('"')
        index = int(index)

        self.memory = memory
        self.index = index

class Command:

    def __init__(self, name: str, command: bytes):
        self.name = name
        self.command = command
        self.date = datetime.utcnow()
        self.sent = None

    def __str__(self):
        return f'Command: {self.name} ({self.command})'

class ReadMessageCommand(Command):

    def __init__(self, index):
        super().__init__('ReadMessage', f'AT+CMGR={index}'.encode())
        self.index = index

RESPONSE_PREFIXES = [
    (b'OK', OKResponse),
    (b'+CMTI', CMTIResponse)
]

class ATModem:

    def __init__(self, device: str, baudrate: int, received_message_handler=None):
        self.device = device
        self.baudrate = baudrate
        self.received_message_handler = received_message_handler

        self.response_buffer = deque([])

        self._close = False
        self.lock = asyncio.Lock()

        self.logger = logging.getLogger('ATModem')

    async def connect(self):
        self.reader, self.writer = await serial_asyncio.open_serial_connection(
            url=self.device,
            baudrate=self.baudrate
        )
        self.logger.debug(f'Connected to {self.device}')

        while not self._close:
            try:
                response = await self.reader.readuntil(RESP_TERMINATOR)
                response = response.rstrip(RESP_TERMINATOR)
                if response:
                    self._resp_handler(response)
            except IncompleteReadError:
                self.logger.warning('Read was interrupted')
                continue

    async def close(self):
        self._close = True
        self.writer.close()
        await self.writer.wait_closed()

    def _resp_handler(self, response):
        self.logger.debug(f'Received response: {response}')
        for prefix in RESPONSE_PREFIXES:
            if response.startswith(prefix[0]):
                response = prefix[1](response=response)
                self.logger.debug(response)
                if isinstance(response, CMTIResponse):
                    self.lock.release()
                    asyncio.ensure_future(self.read_message(response.index))
                self.response_buffer.append(response)
                return

    async def read_message(self, index):
        command = ReadMessageCommand(index)
        await self.send_command(command)

    async def send_command(self, command: Type[Command], timeout: int = 1):
        await self.lock.acquire()
        self.writer.write(command.command + EOL_SEQ)
        await self.writer.drain()
        self.logger.debug(command)
