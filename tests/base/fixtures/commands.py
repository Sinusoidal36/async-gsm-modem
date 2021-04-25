import pytest
from async_gsm_modem.base.command import Command, ExtendedCommand

@pytest.fixture
def command_at():
    return (Command(b'AT'), [b'OK'])

@pytest.fixture
def command_list_messages():
    return (
        ExtendedCommand(b'AT+CMGL').write(b'4'),
        [
            b'+CMGL: 0,0,,51',
            b'07912160130350F7040B915110338063F800001240227182648A24355C6C269BC5662DB218566BD1CCE15B0B57C3CD5AE41AB9268E996530721807',
            b'+CMGL: 1,0,,51',
            b'07912160130350F7040B915110338063F800001240227182648A24355C6C269BC5662DB218566BD1CCE15B0B57C3CD5AE41AB9268E996530721807',
            b'OK'
        ]
    )

@pytest.fixture(params=['command_at','command_list_messages'])
def generic_test_command(request):
    return request.getfixturevalue(request.param)