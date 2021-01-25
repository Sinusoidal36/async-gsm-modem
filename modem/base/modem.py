import asyncio
from asyncio.exceptions import IncompleteReadError
from datetime import datetime
import serial_asyncio
from collections import deque
from typing import Type, Callable, List
from .command import Command
from .response import Response
import logging

class ATModem:

    RESP_SEPERATOR = b'\r\n'
    RESP_TERMINATOR = b'OK'
    CMD_TERMINATOR = b'\r'

    def __init__(self, device: str, baud_rate: int, urc: List[bytes] = None):
        self.device = device
        self.baud_rate = baud_rate

        self.urc = urc if urc else []
        self.urc_buffer = deque()

        self._close = False
        self._lock = asyncio.Lock()
        self.read_loop_task = None

        self.logger = logging.getLogger('ATModem')

    async def connect(self):
        self.reader, self.writer = await serial_asyncio.open_serial_connection(
            url=self.device,
            baudrate=self.baud_rate
        )
        self.logger.debug(f'Connected to {self.device}')
        self.start_read_loop()

    async def lock(self):
        await self.stop_read_loop()
        await self._lock.acquire()
        self.logger.debug('Locked')

    def unlock(self):
        self._lock.release()
        self.start_read_loop()
        self.logger.debug('Unlocked')

    async def write(self, command: Type[Command], terminator: bytes = None):
        terminator = terminator if terminator else self.CMD_TERMINATOR
        self.writer.write(bytes(command)+terminator)
        await self.writer.drain()
        self.logger.debug(command)

    async def send_command(self, command: Type[Command]) -> List[Response]:
        await self.lock()
        await self.write(command)
        responses = await self.read()
        self.unlock()
        return responses

    async def read(self, seperator: bytes = None, terminator: bytes = None, timeout: int = 5) -> List[Response]:
        seperator = seperator if seperator != None else self.RESP_SEPERATOR
        terminator = terminator if terminator != None else self.RESP_TERMINATOR
        responses = []
        while True:
            response = await self.read_response(seperator, timeout)
            if any([bytes(response).startswith(urc) for urc in self.urc]):
                self.urc_buffer.appendleft(response)
            else:
                responses.append(response)
            if (bytes(response) == terminator) or response is None:
                return responses

    async def read_response(self, seperator: bytes = None, timeout: int = 5) -> Response:
        seperator = seperator if seperator != None else self.RESP_SEPERATOR
        try:
            response = await asyncio.wait_for(self.reader.readuntil(seperator), timeout)
            response = Response(response.rstrip(seperator))
            self.logger.debug(response)
            return response
        except IncompleteReadError:
            return
        except asyncio.TimeoutError:
            return

    async def close(self):
        self._close = True
        self.writer.close()
        await self.writer.wait_closed()

    async def urc_handler(self, response: Type[Response]) -> None:
        pass

    async def read_loop(self):
        while True:
            try:
                while self.urc_buffer:
                    response = urc_buffer.pop()
                    await self.urc_handler(response)

                response = await self.read_response()
                if response:
                    await self.urc_handler(response)
            except asyncio.CancelledError:
                return

    def start_read_loop(self):
        self.read_loop_task = asyncio.create_task(self.read_loop())

    async def stop_read_loop(self):
        if self.read_loop_task:
            self.read_loop_task.cancel()
            try:
                await self.read_loop_task
            except asyncio.CancelledError:
                return