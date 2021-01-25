import asyncio
import logging
import sys
from modem.quectel_ec25 import Modem

async def example(modem):
    await modem.connect()
    await modem.ping()
    while True:
        for message in await modem.list_messages('RECEIVED_UNREAD'):
            print(message)
        await asyncio.sleep(5)
    await modem.close()

def main():
    loop = asyncio.get_event_loop()
    modem = Modem('/dev/ttyUSB2', 115200)
    try:
        loop.run_until_complete(example(modem))
    except KeyboardInterrupt:
        loop.run_until_complete(modem.close())

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()