import oi

program = oi.Program('An example program', 'ipc:///tmp/program.sock')
program.add_command('ping', lambda p: 'pong')
program.add_command('state', lambda p: p.state)
program.run()
