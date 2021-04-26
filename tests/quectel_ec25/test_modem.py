import pytest
import logging
from async_gsm_modem.quectel_ec25.modem import Modem
from async_gsm_modem.base.command import Command, ExtendedCommand
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
async def modem(mocker):
    mocker.patch.object(Modem, 'start_read_loop', return_value=None)
    modem = Modem('/dev/ttyXRUSB2', 115200)
    modem.at_logger.setLevel(logging.DEBUG)
    await modem.connect()
    yield modem
    await modem.close()

def test_init():
    modem = Modem('/dev/ttyXRUSB2', 115200)
    assert modem

@pytest.mark.asyncio
async def test_ping(mocker, modem):
    expected_response = [b'AT', b'OK']
    mocker.patch.object(DummyReader, 'readuntil', side_effect=expected_response)

    assert await modem.ping()

@pytest.mark.asyncio
async def test_product_info(mocker, modem):
    expected_response = [b'ATI', b'Quectel', b'', b'OK']
    mocker.patch.object(DummyReader, 'readuntil', side_effect=expected_response)

    product_info = await modem.product_info()