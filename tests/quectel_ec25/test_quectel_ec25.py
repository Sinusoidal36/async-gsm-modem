import pytest
import logging
from async_gsm_modem.quectel_ec25.modem import Modem
from async_gsm_modem.quectel_ec25.info import ProductInfo
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

@pytest.fixture(autouse=True)
def mock_serial_connection(mocker):
    mocker.patch.object(serial_asyncio, 'open_serial_connection', return_value=(DummyReader(), DummyWriter()))

@pytest.fixture
async def modem(mocker):
    mocker.patch.object(Modem, 'start_read_loop', return_value=None)
    mocker.patch.object(Modem, 'initialize', return_value=None)
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
    mocker.patch.object(DummyReader, 'readuntil', side_effect=[b'OK'])

    assert await modem.ping()

@pytest.mark.asyncio
async def test_product_info(mocker, modem):
    expected_response = [b'Quectel', b'EC25', b'Revision: EC25AFFAR07A08M4G', b'OK']
    mocker.patch.object(DummyReader, 'readuntil', side_effect=expected_response)

    product_info = await modem.product_info()
    assert product_info == ProductInfo(manufacturer='Quectel', model='EC25', revision='EC25AFFAR07A08M4G')

@pytest.mark.asyncio
async def test_read_message(mocker, modem):
    expected_response = [b'+CMGR: 0,,23', b'07912160130350F7040B912108378482F500001240625104958A04D4F29C0E', b'OK']
    mocker.patch.object(DummyReader, 'readuntil', side_effect=expected_response)

    message = await modem.read_message(0)
    assert message

@pytest.mark.asyncio
async def test_read_message_no_message(mocker, modem):
    expected_response = [b'OK']
    mocker.patch.object(DummyReader, 'readuntil', side_effect=expected_response)

    message = await modem.read_message(0)
    assert not message

@pytest.mark.asyncio
async def test_read_message_error(mocker, modem):
    expected_response = [b'+CMS ERROR: 300']
    mocker.patch.object(DummyReader, 'readuntil', side_effect=expected_response)

    message = await modem.read_message(0)
    assert not message

@pytest.mark.asyncio
async def test_list_messages(mocker, modem):
    expected_response = [b'+CMGL: 0,0,,23', b'07912160130350F7040B912108378482F500001240625104958A04D4F29C0E', b'+CMGL: 1,0,,23', b'07912160130350F7040B912108378482F500001240625104958A04D4F29C0E', b'OK']
    mocker.patch.object(DummyReader, 'readuntil', side_effect=expected_response)

    messages = await modem.list_messages()
    assert len(messages) == 2

@pytest.mark.asyncio
async def test_list_messages_no_messages(mocker, modem):
    expected_response = [b'OK']
    mocker.patch.object(DummyReader, 'readuntil', side_effect=expected_response)

    messages = await modem.list_messages()
    assert isinstance(messages, list)
    assert not messages