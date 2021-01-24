import asyncio
from asyncio.exceptions import IncompleteReadError
from datetime import datetime
import serial_asyncio
from collections import deque
from typing import Type, Callable, List
from .command import Command
from .response import Response, UnsolicitedResponse
from .response_mapper import ResponseMapper
import logging

class ATModem:

    RESP_SEPERATOR = b'\r\n'
    CMD_TERMINATOR = b'\r'

    def __init__(
        self,
        device: str,
        baud_rate: int,
        response_mapper: Type[ResponseMapper],
        ):
        self.device = device
        self.baud_rate = baud_rate

        self.response_mapper = response_mapper
        
        self.unsolicited_response_buffer = deque()

        self._close = False
        self.lock = asyncio.Lock()
        self.read_loop_task = None

        self.logger = logging.getLogger('ATModem')

    async def connect(self):
        self.reader, self.writer = await serial_asyncio.open_serial_connection(
            url=self.device,
            baudrate=self.baud_rate
        )
        self.logger.debug(f'Connected to {self.device}')
        self.start_read_loop()

    async def close(self):
        self._close = True
        self.writer.close()
        await self.writer.wait_closed()

    async def unsolicited_response_handler(self, response: Type[Response]) -> None:
        pass

    async def read_loop(self) -> None:
        try:
            while self.unsolicited_response_buffer:
                response = unsolicited_response_buffer.pop()
                await self.unsolicited_response_handler(response)

            response = await self.read_response()
            await self.unsolicited_response_handler(response)
            if not self._close:
                self.read_loop_task = asyncio.create_task(self.read_loop())
        except asyncio.CancelledError:
            self.logger.debug('Read Loop Cancelled')
        finally:
            return

    def start_read_loop(self) -> None:
        self.read_loop_task = asyncio.create_task(self.read_loop())

    async def stop_read_loop(self) -> None:
        if self.read_loop_task:
            self.read_loop_task.cancel()
            try:
                await self.read_loop_task
            except asyncio.CancelledError:
                return
    
    async def read_response(self) -> Response:
        try:
            response = await self.reader.readuntil(self.RESP_SEPERATOR)
            response = response.rstrip(self.RESP_SEPERATOR)
            response = self.response_mapper.map(response)
            self.logger.debug(response)
            return response
        except IncompleteReadError:
            pass
            #self.logger.warning('Read was interrupted')

    async def send_command(self, command: Type[Command], timeout: float = 5) -> List[Response]:
        await self.stop_read_loop()
        
        await self.lock.acquire()
        self.writer.write(command.command + self.CMD_TERMINATOR)
        await self.writer.drain()
        self.logger.debug(command)
        responses = []
        while True:
            try:
                response = await asyncio.wait_for(self.read_response(), timeout)
                if isinstance(response, UnsolicitedResponse):
                    self.unsolicited_response_buffer.appendleft(response)
                elif response.response == command.response_terminator:
                    break
                else:
                    responses.append(response)
            except asyncio.TimeoutError:
                self.logger.error(f'{command} timed out')
                break
        self.lock.release()
        self.start_read_loop()

        assert responses[0].response == command.command, Exception('Received response to wrong command')

        return responses[1:]