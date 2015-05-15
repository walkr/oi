import oi


def main():
    program = oi.Program('my program', 'ipc:///tmp/programd.sock')

    program.add_command(
        'ping', lambda: 'pong')
    program.add_command(
        'state', lambda: program.state, 'show program state')
    program.add_command(
        'touch', lambda: setattr(program.state, 'touch', True) and True,
        'touch state')

    program.run()

if __name__ == '__main__':
    main()
