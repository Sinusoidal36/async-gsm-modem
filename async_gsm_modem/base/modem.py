import asyncio
from asyncio.exceptions import IncompleteReadError
from datetime import datetime
import serial_asyncio
from typing import Type, Callable, List
from .command import Command
from .response import Response
import logging

class ATModem:

    RESP_SEPERATOR = b'\r\n'
    RESP_TERMINATOR = b'OK'
    CMD_TERMINATOR = b'\r'

    def __init__(self, device: str, baud_rate: int, urc: List[bytes] = []):
        self.device = device
        self.baud_rate = baud_rate

        self.urc = set(urc) if urc else set()
        self.urc_buffer = []

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
        self.urc_handler_loop_task = asyncio.create_task(self.urc_handler_loop())

    async def close(self):
        await self.stop_read_loop()
        await self.stop_urc_handler_loop()
        self.writer.close()
        await self.writer.wait_closed()

    async def lock(self):
        await self.stop_read_loop()
        await self._lock.acquire()
        self.logger.debug('Locked')

    def unlock(self):
        self._lock.release()
        self.start_read_loop()
        self.logger.debug('Unlocked')

    async def write(self, command: Command, terminator: bytes = None):
        terminator = terminator if terminator else self.CMD_TERMINATOR
        self.writer.write(bytes(command)+terminator)
        await self.writer.drain()
        self.logger.debug(command)

    async def send_command(self, command: Command) -> List[bytes]:
        try:
            await self.lock()
            await self.write(command)
            return await self.read()
        except Exception as e:
            self.logger.error(f'Failed to send command: {command}', exc_info=True)
            return []
        finally:
            self.unlock()

    async def read(self, seperator: bytes = None, terminator: bytes = None, timeout: int = 5) -> List[bytes]:
        seperator = seperator if seperator else self.RESP_SEPERATOR
        terminator = terminator if terminator else self.RESP_TERMINATOR
        responses = []
        while True:
            response = await self.read_response(seperator, timeout)
            if not response:
                return responses
            if any([response.startswith(urc) for urc in self.urc]):
                self.urc_buffer.append(response)
            else:
                responses.append(response)
            if (response == terminator):
                return responses

    async def read_response(self, seperator: bytes = None, timeout: int = 5) -> bytes:
        seperator = seperator if seperator else self.RESP_SEPERATOR
        try:
            response = await asyncio.wait_for(self.reader.readuntil(seperator), timeout)
            response = response.rstrip(seperator)
            self.logger.debug(response)
            return response
        except IncompleteReadError:
            self.logger.debug('Read was canceled before completion')
        except asyncio.TimeoutError:
            self.logger.debug('Read timed out before receiving a response')

    async def urc_handler_loop(self) -> None:
        while True:
            try:
                if self.urc_buffer:
                    self.logger.debug(self.urc_buffer.pop(0))
            except asyncio.CancelledError:
                raise
            except:
                pass
            await asyncio.sleep(0.1)

    async def stop_urc_handler_loop(self) -> None:
        if self.urc_handler_loop_task:
            self.urc_handler_loop_task.cancel()
            try:
                await self.urc_handler_loop_task
            except asyncio.CancelledError:
                return
                
    async def read_loop(self):
        if self._lock.locked():
            return
        while True:
            try:
                response = await self.read_response()
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
