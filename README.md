# asyncio-gsm-modem

asyncio-gsm-modem is a Python library for controlling an AT GSM modem.

## Installation

```bash
pip3 install asyncio-gsm-modem
```

## Usage

```python
import asyncio
from modem.quectel_ec25 import Modem

async def example():
  modem = Modem('/dev/ttyUSB2', 115200)
  await modem.connect()
  await modem.ping()
  for message in await modem.list_messages():
    print(message)
  await modem.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(example())

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[Apache 2](https://choosealicense.com/licenses/apache-2.0/)
