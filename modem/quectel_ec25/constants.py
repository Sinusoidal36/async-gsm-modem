
STATUS_MAP = {
    'RECEIVED_UNREAD': b'0',
    'RECEIVED_READ': b'1',
    'STORED_UNSENT': b'2',
    'STORED_SENT': b'3',
    'ALL': b'4'
}

STATUS_MAP_R = {
    b'0': 'RECEIVED_UNREAD',
    b'1': 'RECEIVED_READ',
    b'2': 'STORED_UNSENT',
    b'3': 'STORED_SENT',
    b'4': 'ALL'
}

DELETE_FLAG = {
    'ALL_READ': b'1',
    'READ_AND_SENT': b'2',
    'READ_AND_UNSENT': b'3',
    'ALL': b'4'
}

UNSOLICITED_RESULT_CODES = [
    b'+CREG',
    b'+CGREG',
    b'+CTZV',
    b'+CTZE',
    b'+CMTI',
    b'+CMT',
    b'^HCMT',
    b'+CBM',
    b'+CDS',
    b'+CDSI',
    b'^HCDS',
    b'+COLP',
    b'+CLIP',
    b'+CRING',
    b'+CCWA',
    b'+CSSI',
    b'+CSSU',
    b'+CUSD',
    b'RDY',
    b'+CFUN',
    b'+CPIN',
    b'+QIND',
    b'POWERED DOWN',
    b'+CGEV'
]