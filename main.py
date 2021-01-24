import asyncio
import logging
import sys
from modem.quectel_ec25 import Modem

async def test(modem):
    await modem.connect()
    await modem.ping()
    messages = await modem.list_messages()
    for message in messages:
        print(message.to_dict())
    await modem.close()

def main():
    loop = asyncio.get_event_loop()
    modem = Modem('/dev/ttyUSB2', 115200)
    try:
        loop.run_until_complete(test(modem))
    except KeyboardInterrupt:
        loop.run_until_complete(modem.close())

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()