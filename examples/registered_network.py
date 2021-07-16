import asyncio
import logging
import sys
from async_gsm_modem.quectel_ec25 import Modem

async def example():
    modem = Modem('/dev/ttyUSB2', 115200)
    await modem.connect()
    await modem.ping()
    print(await modem.registered_network())
    await modem.close()

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(example())

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()
