import sys
import argparse
import threading
import readline
import logging

from colorama import Fore
from nanoservice import Service
from nanoservice import Client

from . import version
from . import worker
from . import compat
from . import util

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
        """ Create a command line argument parser

        Add a few default flags, such as --version
        for displaying the program version when invoked """

        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument(
            '--version', help='show version and exit',
            default=False, action='store_true')
        parser.add_argument(
            '--debug', help='enable debugging',
            default=False, action='store_true')
        return parser

    def add_command(self, command, function, description=None):
        """ Register a new function with a the name `command` and
        `description` (which will be shown then help is invoked). """

        self.registered[command] = {
            'function': function, 'description': description
        }

    def run(self, args=None):
        """ Parse command line arguments if necessary then run program.
        By default this method will just take of the --version flag.

        The logic for other flags should be handled by your subclass """

        args = args or self.parser.parse_args()

        if args.debug:
            logging.basicConfig(level=logging.DEBUG)

        if args.version:
            print(version.VERSION)
            sys.exit(0)


class Program(BaseProgram):
    """ Long running program with a nanoservice endpoint.

    `service` - nanoservice Service object
    `config` - the configuration parsed from --config <filepath> """

    def __init__(self, description, address):
        super(Program, self).__init__(description, address)

        self.service = Service(address) if address else None
        self.config = compat.configparser.ConfigParser()

        # Add the flag for parsing configuration file
        self.parser.add_argument(
            '--config', help='configuration file to use', nargs='?')

        if self.service is None:
            return

        # Add default service worker, which will respond to ctl commands
        # Other workers will perform other kind of work, such as
        # fetching resources from the web, etc
        self.workers.append(worker.ServiceWorker(self.service))

        # Add default commands
        self.add_command('ping', lambda: 'pong')
        self.add_command('help', self.help_function)

    def help_function(self, command=None):
        """ Show help for all available commands or just a single one """
        if command:
            return self.registered[command].get(
                'description', 'No help available'
            )
        return ', '.join(sorted(self.registered))

    def add_command(self, command, function, description=None):
        """ Register a new function for command """
        super(Program, self).add_command(command, function, description)
        self.service.register(command, function)

    def run(self, args=None):
        """ Parse comand line arguments/flags and run program """

        args = args or self.parser.parse_args()
        super(Program, self).run(args)

        # Read configuration file if any
        if args.config is not None:
            filepath = args.config
            self.config.read(filepath)

        # Start workers then wait until they finish work
        [w.start() for w in self.workers]
        [w.join() for w in self.workers]


class ClientWrapper(object):
    """ An wrapper over nanoservice.Client to deal with one or multiple
    clients in a similar fasion """

    def __init__(self, address, timeout):
        self.c = self.create_client(address, timeout)

    def create_client(self, addr, timeout):
        """ Create client(s) based on addr """

        def make(addr):
            c = Client(addr)
            c.socket._set_recv_timeout(timeout)
            return c

        if ',' in addr:
            addrs = addr.split(',')
            addrs = [a.strip() for a in addrs]
            return {a: make(a) for a in addrs}
        return make(addr)

    def _call_single(self, client, command, *args):
        """ Call single """
        try:
            return client.call(command, *args)
        except Exception as e:
            return None, str(e)

    def _call_multi(self, clients, command, *args):
        """ Call multi """
        responses, errors = {}, {}
        for addr, client in clients.items():
            res, err = self._call_single(client, command, *args)
            responses[addr] = res
            errors[addr] = err
        return responses, errors

    def call(self, command, *args):
        """ Call remote service(s) """
        if isinstance(self.c, dict):
            return self._call_multi(self.c, command, *args)
        return self._call_single(self.c, command, *args)

    def is_multi(self):
        """ Does this object include multiple clients """
        return isinstance(self.c, dict)

    def close(self):
        """ Close socket(s) """
        if isinstance(self.c, dict):
            for client in self.c.values():
                client.sock.close()
            return
        self.c.socket.close()


class Response(object):
    """ A local or remote response for a command """

    def __init__(self, kind, res, err, multi=False):
        super(Response, self).__init__()
        self.kind = kind
        self.res = res
        self.err = err
        self.multi = multi

    def _show(self, res, err, prefix='', colored=False):
        """ Show result or error """

        if self.kind is 'local':
            what = res if not err else err
            print(what)
            return

        if self.kind is 'remote':
            if colored:
                red, green, reset = Fore.RED, Fore.GREEN, Fore.RESET
            else:
                red = green = reset = ''
            if err:
                what = prefix + red + 'remote err: {}'.format(err) + reset
            else:
                what = prefix + green + str(res) + reset
            print(what)

    def show(self):
        if self.multi:
            for addr in self.res:
                self._show(
                    self.res[addr], self.err[addr],
                    prefix='- {}: '.format(addr), colored=True
                )
            return
        self._show(self.res, self.err)


class CtlProgram(BaseProgram):
    """ The Ctl program

    Note:

        When a CtlProgram accepts a command it will make a request
        to the remote service with that command and any args extracted.

        When we add commands via `add_command` method, then those
        commands will be executed by our registered function; they will
        be not dispatched to the remote service. This is helpful, because
        it allows us to register certain local commands, such as `quit`, etc

     """

    def __init__(self, description, address, timeout=3000):
        super(CtlProgram, self).__init__(description, address)
        self.client = ClientWrapper(address, timeout) if address else None

        # Add command argument
        self.parser.add_argument(
            'command', help='command name to execute', nargs='*',
            metavar='command')

        # Add default commands
        self.add_command('quit', lambda p: sys.exit(0), 'quit ctl')

    def call(self, command, *args):
        """ Execute local OR remote command and show response """

        if not command:
            return

        # Look for local methods first
        try:
            res = self.registered[command]['function'](self, *args)
            return Response('local', res, None)

        # Method not found, try remote
        except KeyError:

            # Execute remote command
            res, err = self.client.call(command, *args)
            return Response('remote', res, err, self.client.is_multi())

        # Local exception
        except Exception as e:
            return Response('local', res, str(e))

    def parse_input(self, text):
        """ Parse ctl user input. Double quotes are used
        to group together multi words arguments. """

        parts = util.split(text)
        command = parts[0] if text and parts else None
        command = command.lower() if command else None
        args = parts[1:] if len(parts) > 1 else []

        return (command, args)

    def loop(self):
        """ Enter loop, read user input then run command. Repeat """

        while True:
            text = compat.input('ctl > ')
            command, args = self.parse_input(text)
            if not command:
                continue
            response = self.call(command, *args)
            response.show()

    def run(self, args=None, loop=True):

        args = self.parser.parse_args()
        super(CtlProgram, self).run(args)

        # Execute a single command then exit
        if args.command:
            # command will come as a list (zero or more elements)
            # so, extract the first element as the command name
            # and the rest will all be positional arguments
            command = args.command[0]
            args = args.command[1:] if len(args.command) > 1 else []
            response = self.call(command, *args)
            response.show()
            sys.exit(0)

        # Enter command loop
        if loop:
            self.loop()
