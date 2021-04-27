import pytest
import logging
from async_gsm_modem.base.modem import ATModem
from async_gsm_modem.base.command import Command
from async_gsm_modem.base.response import Response
from async_gsm_modem.base.exceptions import *
import asyncio
import serial_asyncio

class DummyReader:
    
    async def readuntil(self, *args, **kwargs):
        pass

class DummyWriter:

    def write(self, *args, **kwargs):
        pass

    async def drain(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

    async def wait_closed(self, *args, **kwargs):
        pass

@pytest.fixture(autouse=True)
def mock_serial_connection(mocker):
    mocker.patch.object(serial_asyncio, 'open_serial_connection', return_value=(DummyReader(), DummyWriter()))

@pytest.fixture
async def mock_modem(mocker):
    mocker.patch.object(ATModem, 'start_read_loop', return_value=None)
    mocker.patch.object(ATModem, 'initialize', return_value=None)
    modem = ATModem('/dev/ttyXRUSB2', 115200)
    modem.at_logger.setLevel(logging.DEBUG)
    await modem.connect()
    yield modem
    await modem.close()

def test_init():
    modem = ATModem('/dev/ttyXRUSB2', 115200)
    assert modem

@pytest.mark.asyncio
async def test_connect(mocker):
    mocker.patch.object(ATModem, 'start_read_loop', return_value=None)
    mocker.patch.object(ATModem, 'initialize', return_value=None)
    modem = ATModem('/dev/ttyXRUSB2', 115200)
    await modem.connect()
    assert modem.reader
    assert modem.writer
    await modem.close()

@pytest.mark.asyncio
async def test_connect_fail(mocker):
    mocker.patch.object(ATModem, 'start_read_loop', return_value=None)
    mocker.patch.object(ATModem, 'read', side_effect=asyncio.TimeoutError)

    with pytest.raises(ModemConnectionError):
        modem = ATModem('/dev/ttyXRUSB2', 115200)
        await modem.connect()
        
@pytest.mark.asyncio
async def test_read(mocker, mock_modem):
    mocker.patch.object(DummyReader, 'readuntil', return_value=b'OK\r\n')
    response = await mock_modem.read()
    assert response == b'OK'

@pytest.mark.asyncio
async def test_read_timeout(mocker, mock_modem):
    async def sleep(*args, **kwargs):
        await asyncio.sleep(1)
        return b'OK\r\n'
    mocker.patch.object(DummyReader, 'readuntil', side_effect=sleep)
    exception = None
    with pytest.raises(asyncio.TimeoutError):
        response = await mock_modem.read(timeout=0)

@pytest.mark.asyncio
async def test_send_command(mocker, mock_modem, generic_test_command):
    command, expected_response, terminator = generic_test_command
    mocker.patch.object(DummyReader, 'readuntil', side_effect=expected_response + [terminator])

    response = await mock_modem.send_command(command, response_terminator=terminator, timeout=1)
    assert response == Response(expected_response)

@pytest.mark.asyncio
async def test_send_command_with_urc(mocker, mock_modem, generic_test_command):
    mock_modem.urc = [(b'+CMT', 2)]

    command, expected_response, terminator = generic_test_command
    response_with_urc = expected_response[:-1] + [b'+CMT', b'mock'] + expected_response[-1:] + [terminator]
    mocker.patch.object(DummyReader, 'readuntil', side_effect=response_with_urc)

    response = await mock_modem.send_command(command, response_terminator=terminator, timeout=1)
    assert response == Response(expected_response)
    assert mock_modem.urc_buffer

@pytest.mark.asyncio
async def test_send_command_with_error(mocker, mock_modem, generic_test_command):
    command, expected_response, terminator = generic_test_command
    expected_response = [b'ERROR']
    mocker.patch.object(DummyReader, 'readuntil', side_effect=expected_response + [terminator])

    with pytest.raises(CommandFailed):
        response = await mock_modem.send_command(command, response_terminator=terminator, timeout=1)