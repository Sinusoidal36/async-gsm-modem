import asyncio
import logging
import sys
from modem.at_modem import ATModem, Command

async def test_command(modem):
    await asyncio.sleep(2)
    await modem.send_command(Command(name='AT', command=b'AT'))

def main():
    loop = asyncio.get_event_loop()
    modem = ATModem('/dev/ttyUSB2', 115200)
    try:
        asyncio.ensure_future(modem.connect())
        asyncio.ensure_future(test_command(modem))
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(modem.close())

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    main()