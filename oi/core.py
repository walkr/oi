import sys
import argparse
import threading

from nanoservice import Service
from nanoservice import Client

from . import version
from . import worker
from . import compat


lock = threading.Lock()


class State(dict):
    """ A dot access dictionary """

    def __init__(self, *args, **kwargs):
        super(State, self).__init__(self, *args, **kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError

    def __setattr__(self, key, value):
        lock.acquire()
        self[key] = value
        lock.release()


class BaseProgram(object):
    """ Subclass this """

    def __init__(self, description, address=None, state=None, workers=None):
        self.description = description
        self.address = address
        self.parser = self.new_parser()
        self.state = state or State()
        self.workers = workers or []
        self.registered = {}  # registered commands

    def new_parser(self):
        """ Create argument parser with some defaults """

        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument(
            '--version', help='show version and exit',
            default=False, action='store_true')
        return parser

    def add_command(self, command, function, description=None):
        """ Add local command """

        self.registered[command] = {
            'function': function, 'description': description
        }

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
        self.config = {}

        # Add additional arguments
        self.parser.add_argument(
            '--config', help='configuration file to use', nargs='?')

        if self.service is None:
            return

        # Add default service worker, which will respond to ctl commands
        self.workers.append(worker.ServiceWorker(self.service))

        # Add default commands
        self.add_command('ping', lambda: 'pong')
        self.add_command('help', self.help_function)

    def help_function(self, command=None):
        """ Show help for all or a single command """
        if command:
            return self.registered[command].get(
                'description', 'No help available'
            )
        return ', '.join(self.registered)

    def add_command(self, command, function, description=None):
        """ Register a new function for command """
        super(Program, self).add_command(command, function, description)
        self.service.register(command, function)

    def parse_config(self, filepath):
        """ Parse configuration file """

        config = compat.configparser.ConfigParser()
        config.read(filepath)
        return config

    def run(self, args=None):
        """ Run program. (If not supplied, parse program arguments)"""

        args = args or self.parser.parse_args()
        super(Program, self).run(args)

        if args.version:
            print(version.VERSION)
            sys.exit(0)

        # Read configuration file if any
        if args.config is not None:
            self.config = self.parse_config(args.config)

        # Start workers then wait until they finish work
        [w.start() for w in self.workers]
        [w.join() for w in self.workers]


class CtlProgram(BaseProgram):
    """ The Ctl program

    Note:

        When a CtlProgram accepts a command it will make a request
        to the remote service with that command and any args extracted.

        When we add commands via `add_command` method, then those
        commands will be executed by our registered function; they will
        be not dispatched to the remote service. This is helpfull, because
        it allows us to register certain local commands, such as `quit`, etc

     """

    def __init__(self, description, address):
        super(CtlProgram, self).__init__(description, address)

        self.client = Client(address) if address else None

        # Add command argument
        self.parser.add_argument(
            'command', help='command name to execute', nargs='?',
            metavar='command')

        # Add default commands
        self.add_command('quit', lambda p: sys.exit(0), 'quit ctl')

    def call(self, command, *args):
        """ Execute local OR remote command and show result """

        if not command:
            return

        res, err = None, None

        # Try local first
        try:
            res = self.registered[command]['function'](self, *args)
        except KeyError:

            # Execute remote command
            res, err = self.client.call(command, *args)
            return 'remote', res, err

        except Exception as e:
            return 'local', res, str(e)

        return 'local', res, err

    def show(self, dest, res, err):
        """ Show result OR error """
        if res:
            print(res)

        elif err is not None:
            print('{} err: {}'.format(dest, err))

    def parse_input(self, text):
        """ Parse ctl user input """

        text = text.strip()
        parts = text.split(' ')

        command = parts[0] if text and parts else None
        command = command.lower() if command else None
        args = parts[1:] if len(parts) > 1 else []

        return (command, args)

    def loop(self):
        """ Enter a loop, read user input then run """

        while True:
            text = compat.input('ctl > ')
            command, args = self.parse_input(text)
            if not command:
                continue
            dest, res, err = self.call(command, *args)
            self.show(dest, res, err)

    def run(self, args=None, loop=True):

        args = self.parser.parse_args()
        super(CtlProgram, self).run(args)

        # Execute a single command then exit
        if args.command is not None:
            command, args = self.parse_input(args.command)
            dest, res, err = self.call(command, *args)
            self.show(dest, res, err)
            sys.exit(0)

        # Enter command loop
        if loop:
            self.loop()
