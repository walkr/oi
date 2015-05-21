import sys
import oi


def main():
    addr = sys.argv.pop(1)
    program = oi.Program('my program', addr)

    program.add_command(
        'ping', lambda: 'pong')

    program.add_command(
        'state', lambda: program.state, 'show program state')

    program.add_command(
        'store', lambda key, val: setattr(program.state, key, val) or True,
        'store an item')

    program.add_command(
        'get', lambda key: getattr(program.state, key, None),
        'get an item')

    program.run()

if __name__ == '__main__':
    main()
