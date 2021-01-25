# async-gsm-modem

async-gsm-modem is YetAnother™ Python library for controlling an AT GSM modem using asyncio.



## Installation

```bash
pip3 install async-gsm-modem
```

## Usage

```python
import asyncio
from async_gsm_modem.quectel_ec25 import Modem

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
## TODO

- Fully implement EC25 module
- Implement generic modem class
- MMS functionality
- Testing
- More examples
- Documentation
- Full typing

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[Apache 2](https://choosealicense.com/licenses/apache-2.0/)
