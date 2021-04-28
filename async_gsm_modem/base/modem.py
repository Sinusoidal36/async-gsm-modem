import asyncio
from contextlib import asynccontextmanager
from asyncio.exceptions import IncompleteReadError, TimeoutError, CancelledError
from datetime import datetime
import serial_asyncio
from typing import Type, Callable, List, Tuple
from .command import Command
from .response import Response, UnsolicitedResultCode
from .exceptions import CommandError, CommandFailed, ModemConnectionError
import logging
import re

AT_PATTERN = re.compile(br'^AT(\+[^?=]+)[?=]{1}')

class ATModem:

    RESP_SEPERATOR = b'\r\n'
    RESP_TERMINATOR = b'OK'
    CMD_TERMINATOR = b'\r'
    ERROR_TERMINATOR = b'ERROR'

    def __init__(self, device: str, baud_rate: int, urc: List[Tuple[bytes, int]] = None, error_codes: List[bytes] = None):
        self.device = device
        self.baud_rate = baud_rate

        self.urc = urc if urc else []
        self.urc_buffer = []

        self.error_codes = error_codes if error_codes else []

        self.write_lock = asyncio.Lock()
        self.read_lock = asyncio.Lock()
        self.read_task = None
        self.read_loop_task = None

        self.at_logger = logging.getLogger('ATModem')

    async def initialize(self) -> None:
        await self.send_command(Command(b'AT'))
        await self.send_command(Command(b'ATE0'))
    
    async def connect(self) -> None:
        self.reader, self.writer = await serial_asyncio.open_serial_connection(
            url=self.device,
            baudrate=self.baud_rate
        )
        self.at_logger.debug(f'Connected to {self.device}')
        try:
            await self.initialize()
        except Exception as e:
            self.at_logger.error('Failed to connect to modem', exc_info=True)
            raise ModemConnectionError from e
        self.start_read_loop()
        self.start_urc_handler_loop()

    async def close(self) -> None:
        await self.stop_read_loop()
        await self.stop_urc_handler_loop()
        self.writer.close()
        await self.writer.wait_closed()
        self.at_logger.debug(f'Modem closed')

    async def write(self, command: Command, terminator: bytes = None) -> None:
        terminator = terminator if terminator else self.CMD_TERMINATOR
        self.writer.write(bytes(command)+terminator)
        await self.writer.drain()
        self.at_logger.debug(command)

    async def read(self, seperator: bytes = None, timeout: int = 5) -> bytes:
        seperator = seperator if seperator else self.RESP_SEPERATOR
        async with self.read_lock:
            try:
                self.read_task = asyncio.create_task(self.reader.readuntil(seperator))
                data = await asyncio.wait_for(self.read_task, timeout)
                return data.rstrip(seperator) if data else None
            except IncompleteReadError:
                self.at_logger.debug('Read was canceled before completion')

    async def cancel_read(self) -> None:
        if self.read_task and not self.read_task.done():
            self.read_task.cancel()
            try:
                await self.read_task
            except CancelledError:
                return

    async def send_command(self, command: Command, response_terminator: bytes = None, timeout: int = 5) -> List[bytes]:
        try:
            async with self.write_lock:
                # if we acquire a write lock but have a read going, cancel it
                await self.cancel_read()

                await self.write(command)
                extended_command = AT_PATTERN.match(bytes(command))
                expected_response = extended_command.group(1) if extended_command else None
                response = await self.read_response(expected_response=expected_response, terminator=response_terminator, timeout=timeout)
                self.at_logger.debug(response)
                return response
        except Exception as e:
            self.at_logger.error(f'Failed to send command: {command}', exc_info=True)
            raise CommandFailed from e

    async def read_response(self, expected_response: bytes = None, seperator: bytes = None, terminator: bytes = None, timeout: int = 5) -> Response:
        seperator = seperator if seperator else self.RESP_SEPERATOR
        terminator = terminator if terminator else self.RESP_TERMINATOR
        response_chunks = []
        while True:
            try:
                response_chunk = await self.read(seperator, timeout)
            except:
                self.at_logger.debug(f'Read error, partial response: {response_chunks}')
                raise

            error_code = next(filter(lambda error_code: response_chunk.startswith(error_code), self.error_codes), None)
            if error_code or response_chunk == self.ERROR_TERMINATOR:
                raise CommandError(error=response_chunk)

            # if URC was received read it out and push to urc buffer then continue processing expected response
            urc = next(filter(lambda x: response_chunk.startswith(x[0]), self.urc), None)
            expected = response_chunk.startswith(expected_response) if expected_response else False
            if urc and not expected:
                try:
                    code, n_chunks = urc
                    self.at_logger.debug(f'Received URC: {code}')
                    urc_chunks = [response_chunk]
                    for n in range(n_chunks - 1):
                        urc_chunks.append(await self.read(seperator))
                    self.urc_buffer.append(UnsolicitedResultCode(chunks=urc_chunks, code=code))
                except (CancelledError, TimeoutError):
                    raise
                except:
                    self.at_logger.error('URC was received but failed to process', exc_info=True)
                    raise
            elif response_chunk is None or response_chunk == terminator:
                break
            elif response_chunk:
                response_chunks.append(response_chunk)

        return Response(response_chunks)

    async def urc_handler_loop(self) -> None:
        while True:
            try:
                if self.urc_buffer:
                    await self.urc_handler(self.urc_buffer.pop(0))
            except CancelledError:
                raise
            except Exception as e:
                self.at_logger.error(e, exc_info=True)
            await asyncio.sleep(0.1)

    def start_urc_handler_loop(self) -> None:
        self.urc_handler_loop_task = asyncio.create_task(self.urc_handler_loop())

    async def stop_urc_handler_loop(self) -> None:
        if self.urc_handler_loop_task:
            self.urc_handler_loop_task.cancel()
            try:
                await self.urc_handler_loop_task
            except CancelledError:
                return

    async def urc_handler(self, response: UnsolicitedResultCode) -> None:
        pass
                
    async def read_loop(self):
        while True:
            try:
                if not self.write_lock.locked() and not self.read_lock.locked():
                    response = await self.read_response()
                    if response:
                        self.at_logger.warn(f'Unexpected response received: {response}')
            except TimeoutError:
                pass
            await asyncio.sleep(0.1)

    def start_read_loop(self):
        self.read_loop_task = asyncio.create_task(self.read_loop())

    async def stop_read_loop(self):
        if self.read_loop_task:
            self.read_loop_task.cancel()
            try:
                await self.read_loop_task
            except CancelledError:
                self.at_logger.debug('Read loop cancelled successfully')
                return True
