import asyncio
import pytest

class MockQuectelEC25:

    def __init__(self, echo: bool = True):
        self.echo = echo