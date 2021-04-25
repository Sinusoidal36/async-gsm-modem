import asyncio
from asyncio.exceptions import IncompleteReadError
from datetime import datetime
import serial_asyncio
from typing import Type, Callable, List, Tuple
from .command import Command
from .response import Response, UnsolicitedResultCode
import logging

class ATModem:

    RESP_SEPERATOR = b'\r\n'
    RESP_TERMINATOR = b'OK'
    CMD_TERMINATOR = b'\r'

    def __init__(self, device: str, baud_rate: int, urc: List[Tuple[str, int]] = None):
        self.device = device
        self.baud_rate = baud_rate

        self.urc = urc if urc else []
        self.urc_buffer = []

        self._close = False
        self._lock = asyncio.Lock()
        self.read_loop_task = None

        self.at_logger = logging.getLogger('ATModem')

    async def connect(self):
        self.reader, self.writer = await serial_asyncio.open_serial_connection(
            url=self.device,
            baudrate=self.baud_rate
        )
        self.at_logger.debug(f'Connected to {self.device}')
        self.start_read_loop()
        self.start_urc_handler_loop()

    async def close(self):
        await self.stop_read_loop()
        await self.stop_urc_handler_loop()
        self.writer.close()
        await self.writer.wait_closed()

    async def lock(self):
        await self.stop_read_loop()
        await self._lock.acquire()
        self.at_logger.debug('Locked')

    def unlock(self):
        self._lock.release()
        self.start_read_loop()
        self.at_logger.debug('Unlocked')

    async def write(self, command: Command, terminator: bytes = None):
        terminator = terminator if terminator else self.CMD_TERMINATOR
        self.writer.write(bytes(command)+terminator)
        await self.writer.drain()
        self.at_logger.debug(command)

    async def read(self, seperator: bytes = None, timeout: int = 5) -> bytes:
        seperator = seperator if seperator else self.RESP_SEPERATOR
        try:
            data = await asyncio.wait_for(self.reader.readuntil(seperator), timeout)
            return data.rstrip(seperator)
        except IncompleteReadError:
            self.at_logger.debug('Read was canceled before completion')

    async def send_command(self, command: Command, timeout: int = 5) -> List[bytes]:
        try:
            await self.lock()
            await self.write(command)
            return await asyncio.wait_for(self.read_response(), timeout)
        except Exception as e:
            self.at_logger.error(f'Failed to send command: {command}', exc_info=True)
            return []
        finally:
            self.unlock()

    async def read_response(self, seperator: bytes = None, terminator: bytes = None, timeout: int = 5) -> Response:
        seperator = seperator if seperator else self.RESP_SEPERATOR
        terminator = terminator if terminator else self.RESP_TERMINATOR
        response_chunks = []
        while True:
            response_chunk = await self.read(seperator, timeout)

            if not response_chunk:
                break

            # if URC was received read it out and push to urc buffer then continue processing expected response
            urc = next(filter(lambda x: response_chunk.startswith(x[0]), self.urc), None)
            if urc:
                try:
                    code, n_chunks = urc
                    self.at_logger.debug(f'Received URC: {code}')
                    urc_chunks = [response_chunk]
                    for n in range(n_chunks - 1):
                        urc_chunks.append(await self.read())
                    self.urc_buffer.append(UnsolicitedResultCode(chunks=urc_chunks, code=code))
                    continue
                except:
                    self.at_logger.error('URC was received but failed to process', exc_info=True)
            else:
                response_chunks.append(response_chunk)

            if response_chunk == terminator:
                break

        if response_chunks:
            response = Response(response_chunks)
            self.at_logger.debug(response)
            return response
        else:
            return

    async def urc_handler_loop(self) -> None:
        while True:
            try:
                if self.urc_buffer:
                    await self.urc_handler(self.urc_buffer.pop(0))
            except asyncio.CancelledError:
                raise
            except:
                pass
            await asyncio.sleep(0.1)

    def start_urc_handler_loop(self) -> None:
        self.urc_handler_loop_task = asyncio.create_task(self.urc_handler_loop())

    async def stop_urc_handler_loop(self) -> None:
        if self.urc_handler_loop_task:
            self.urc_handler_loop_task.cancel()
            try:
                await self.urc_handler_loop_task
            except asyncio.CancelledError:
                return

    async def urc_handler(self, response: UnsolicitedResultCode) -> None:
        pass
                
    async def read_loop(self):
        if self._lock.locked():
            return
        while True:
            try:
                response = await self.read_response()
            except asyncio.TimeoutError:
                pass
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
