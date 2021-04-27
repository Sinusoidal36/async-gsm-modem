import pytest
from async_gsm_modem.base.command import Command, ExtendedCommand

@pytest.fixture
def command_at():
    return (Command(b'AT'), [b'OK'])

@pytest.fixture(params=[
    (b'AT', [b'OK']),
    (b'ATI', [b'Quectel', b'EC25', b'Revision: EC25AFFAR07A08M4G', b'OK']),
    (b'AT+GMI', [b'Quectel', b'OK']),
    (b'AT+GMM', [b'EC25', b'OK']),
    (b'AT+GMR', [b'EC25AFFAR07A08M4G', b'OK']),
    (b'AT+CGMI', [b'Quectel', b'OK']),
    (b'AT+CGMM', [b'EC25', b'OK']),
    (b'AT+CGMR', [b'EC25AFFAR07A08M4G', b'OK']),
    (b'AT+GSN', [b'00000000000000', b'OK']),
    (b'AT+CGSN', [b'00000000000000', b'OK']),
    (b'AT+GSN', [b'00000000000000', b'OK']),
    (b'AT+CGSN', [b'00000000000000', b'OK']),
    (b'AT&V', [b'&C: 1', b'&D: 2', b'&F: 0', b'&W: 0', b'E: 0', b'Q: 0', b'V: 1', b'X: 1', b'Z: 0', b'S0: 0', b'S3: 13', b'S4: 10', b'S5: 8', b'S6: 2', b'S7: 0', b'S8: 2', b'S10: 15', b'OK']),
    (b'AT+CPAS', [b'+CPAS: 0', b'OK']),
    (b'AT+CEER', [b'+CEER: 5,36', b'OK']),
    (b'AT+CIMI', [b'0000000000000000', b'OK']),
    (b'AT+QCCID', [b'+QCCID: 0000000000000000F', b'OK']),
    (b'AT+QINISTAT', [b'+QINISTAT: 7', b'OK']),
    (b'AT+CSQ', [b'+CSQ: 16,99', b'OK']),
    (b'AT+COPN', [b'+COPN: "00101","Test PLMN 1-1"', b'+COPN: "00102","Test PLMN 1-2"', b'+COPN: "00201","Test PLMN 2-1"', b'OK']),
    (b'AT+QLTS', [b'+QLTS: "2021/04/21,07:11:49-28,1"', b'OK']),
    (b'AT+QNWINFO', [b'+QNWINFO: "FDD LTE","310000","LTE BAND 2",1125', b'OK']),
    (b'AT+QSPN', [b'+QSPN: "T-Mobile","T-Mobile","",0,"310000"', b'OK']),
    (b'AT+CNUM', [b'+CNUM: ,"10000000000",129', b'OK']),
])
def command_execution(request):
    return (Command(request.param[0]), request.param[1])