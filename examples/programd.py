import oi

program = oi.Program('my program', 'ipc:///tmp/program.sock')
program.add_command('ping', lambda p: 'pong')
program.add_command('state', lambda p: p.state)
program.run()
