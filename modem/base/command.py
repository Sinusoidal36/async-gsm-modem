from typing import Type
from .response import Response

class Command:

    def __init__(self, command: bytes, response_terminator: bytes):
        self.command = command
        self.response_terminator = response_terminator

    def __str__(self):
        return f'Command({self.command.decode()})'

    def add_response(self, response: Type[Response]):
        if isinstance(response, self.response_terminator):
            self.complete = True
        self.responses.append(response)

    def process_responses(self):
        pass

class ExtendedCommand(Command):

    def test(self) -> Command:
        return Command(
            self.command + b'=?',
            self.response_terminator
        )

    def read(self) -> Command:
        return Command(
            self.command + b'?',
            self.response_terminator
        )

    def write(self, *args: bytes) -> Command:
        return Command(
            (self.command + b'=' + b','.join(args)), 
            self.response_terminator
        )

    def execute(self) -> Command:
        return Command(
            self.command, 
            self.response_terminator
        )