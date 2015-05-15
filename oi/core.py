import sys
import argparse

from nanoservice import Service
from nanoservice import Client

from . import version
from . import worker
from . import compat


class Runner(object):
    """ A Runner is a simple object which maps command names to functions """

    def __init__(self, methods=None):
        self.methods = methods or {}

    def add(self, command, function):
        """ Register a new function for `command` """
        self.methods[command] = function

    def run(self, command, *args):
        """ Run function for `command` with `args` """
        self.methods[command](*args)


class State(dict):
    """ A dot access dictionary """

    def getattr(self, key):
        try:
            return self['key']
        except KeyError:
            raise AttributeError

    def setattr(self, key, value):
        self[key] = value


class BaseProgram(object):
    """ Subclass this """

    def __init__(self, description, address=None, state=None, workers=None):
        self.description = description
        self.address = address
        self.parser = self.new_parser()
        self.runner = Runner()
        self.state = state or State()
        self.workers = workers or []

    def new_parser(self):
        """ Create argument parser with some defaults """

        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument(
            '--version', help='show version and exit',
            default=False, action='store_true')
        return parser

    def run(self, args=None):
        """ Parse arguments if necessary then run program """
        args = args or self.parser.parse_args()

        if args.version:
            print(version.VERSION)
            sys.exit(0)


class Program(BaseProgram):
    """ Long running program with a nanoservice endpoint """

    def __init__(self, description, address):
        super(Program, self).__init__(description, address)
        self.service = Service(address) if address else None
        self.commands = set()

        # Add additional arguments
        self.parser.add_argument(
            '--config', help='configuration file to use', nargs='?')

        if self.service is None:
            return

        # Add default service worker, which will respond to ctl commands
        self.workers.append(worker.ServiceWorker(self.service))

        # Add default commands
        self.add_command(
            'ping', lambda p: 'pong')
        self.add_command(
            'help', lambda p: 'commands: ' + ', '.join(p.commands))

    def add_command(self, command, function):
        """ Register a new function for command.

        The `function` must accept a single argument,
        which will be the current program instance """

        fun = lambda: function(self)
        self.service.register(command, fun)
        self.commands.add(command)

    def run(self, args=None):
        """ Run program. (If not supplied, parse program arguments)"""

        args = args or self.parser.parse_args()
        super(Program, self).run(args)

        if args.version:
            print(version.VERSION)
            sys.exit(0)

        # Read configuration file if any
        if args.config is not None:
            self.config = args.config

        # Start workers then wait until they finish work
        [w.start() for w in self.workers]
        [w.join() for w in self.workers]


class CtlProgram(BaseProgram):
    """ The Ctl program """

    def __init__(self, description, address):
        super(CtlProgram, self).__init__(description, address)
        self.client = Client(address) if address else None

        # Add command argument
        self.parser.add_argument(
            'command', help='command name to execute', nargs='?',
            metavar='command')

    def execute(self, command):
        """ Execute a command """
        self.call(command)

    def call(self, command, *args):
        """ Execute remote command and show result """

        res, err = self.client.call(command, *args)
        if err:
            print('program err: {}'.format(err))
        else:
            print(res)

    def loop(self):
        """ Enter a loop, read user input then run """

        while True:
            command = compat.input('ctl > ')
            command = command.strip().lower()
            if command == 'quit':
                sys.exit(0)
            self.call(command)

    def run(self, args=None, loop=True):

        args = self.parser.parse_args()
        super(CtlProgram, self).run(args)

        # Execute a single command then exit
        if args.command is not None:
            self.execute(args.command)
            sys.exit(0)

        # Enter command loop
        if loop:
            self.loop()
