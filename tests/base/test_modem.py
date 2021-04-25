import pytest
import logging
from async_gsm_modem.base.modem import ATModem
from async_gsm_modem.base.command import Command
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

def response_generator(response, *args, **kwargs):
    for v in response:
        yield v

@pytest.fixture(autouse=True)
def mock_serial_connection(mocker):
    mocker.patch.object(serial_asyncio, 'open_serial_connection', return_value=(DummyReader(), DummyWriter()))

@pytest.fixture
async def mock_modem(mocker):
    mocker.patch.object(ATModem, 'start_read_loop', return_value=None)
    modem = ATModem('/dev/ttyXRUSB2', 115200)
    modem.logger.setLevel(logging.DEBUG)
    await modem.connect()
    yield modem
    await modem.close()

def test_init():
    modem = ATModem('/dev/ttyXRUSB2', 115200)
    assert modem

@pytest.mark.asyncio
async def test_connect(mocker):
    mocker.patch.object(ATModem, 'start_read_loop', return_value=None)
    modem = ATModem('/dev/ttyXRUSB2', 115200)
    await modem.connect()
    assert modem.reader
    assert modem.writer
    await modem.close()

@pytest.mark.asyncio
async def test_send_command(mocker, mock_modem, generic_test_command):
    command, expected_response = generic_test_command
    mocker.patch.object(DummyReader, 'readuntil', side_effect=expected_response)

    response = await asyncio.wait_for(mock_modem.send_command(command), 1)
    assert response == expected_response

@pytest.mark.asyncio
async def test_send_command_with_urc(mocker, mock_modem, generic_test_command):
    mock_modem.urc = set([b'+CMTI'])

    command, expected_response = generic_test_command
    response_with_urc = expected_response[:-1] + [b'+CMTI'] + expected_response[-1:]
    mocker.patch.object(DummyReader, 'readuntil', side_effect=response_with_urc)

    response = await asyncio.wait_for(mock_modem.send_command(command), 1)
    assert response == expected_response
    assert mock_modem.urc_buffer