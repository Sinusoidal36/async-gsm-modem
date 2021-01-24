from typing import Type
from .response import Response

class Command:

    def __init__(
        self, 
        command: bytes,
        response_terminator: bytes,
        response_seperator: bytes = None,
        wait_for_response: bool = True
        ):
        self.command = command
        self.response_terminator = response_terminator
        self.response_seperator = response_seperator
        self.wait_for_response = wait_for_response

    def __str__(self):
        try:
            return f'Command({self.command.decode()})'
        except UnicodeDecodeError:
            return f'Command({self.command})'

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
            self.response_terminator,
            self.response_seperator,
            self.wait_for_response
        )

    def read(self) -> Command:
        return Command(
            self.command + b'?',
            self.response_terminator,
            self.response_seperator,
            self.wait_for_response
        )

    def write(self, *args: bytes) -> Command:
        return Command(
            (self.command + b'=' + b','.join(args)), 
            self.response_terminator,
            self.response_seperator,
            self.wait_for_response
        )

    def execute(self) -> Command:
        return Command(
            self.command, 
            self.response_terminator,
            self.response_seperator,
            self.wait_for_response
        )