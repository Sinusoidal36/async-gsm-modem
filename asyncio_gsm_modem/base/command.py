
class Command:

    def __init__(self, command: bytes):
        self.command = command

    def __str__(self):
        try:
            return f'Command({self.command.decode()})'
        except UnicodeDecodeError:
            return f'Command({self.command})'

    def __bytes__(self):
        return self.command

class ExtendedCommand(Command):

    def test(self) -> Command:
        return Command(
            self.command + b'=?',
        )

    def read(self) -> Command:
        return Command(
            self.command + b'?',
        )

    def write(self, *args: bytes) -> Command:
        return Command(
            (self.command + b'=' + b','.join(args)), 
        )

    def execute(self) -> Command:
        return Command(
            self.command, 
        )