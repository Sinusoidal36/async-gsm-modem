
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

ERROR_CODES = [
    b'+CMS ERROR',
    b'+CME ERROR'
]

# EC25 URC codes with the corresponding chunk count
UNSOLICITED_RESULT_CODES = [
    (b'+CREG', 1),
    (b'+CGREG', 1),
    (b'+CTZV', 1),
    (b'+CTZE', 1),
    (b'+CMTI', 1),
    (b'+CMT', 2),
    (b'^HCMT', 2),
    (b'+CBM', 2),
    (b'+CDS', 1),
    (b'+CDSI', 1),
    (b'^HCDS', 2),
    (b'+COLP', 1),
    (b'+CLIP', 1),
    (b'+CRING', 1),
    (b'+CCWA', 1),
    (b'+CSSI', 1),
    (b'+CSSU', 1),
    (b'+CUSD', 1),
    (b'RDY', 1),
    (b'+CFUN', 1),
    (b'+CPIN', 1),
    (b'+QIND', 1),
    (b'POWERED DOWN', 1),
    (b'+CGEV', 1),
    (b'NO CARRIER', 1)
]