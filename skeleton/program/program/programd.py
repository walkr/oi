import oi


def main():
    program = oi.Program('my program', 'ipc:///tmp/oi-random_string.sock')
    program.add_command('ping', lambda p: 'pong')
    program.add_command('state', lambda p: p.state)
    program.run()

if __name__ == '__main__':
    main()
