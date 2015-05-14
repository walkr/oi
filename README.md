oi
==
python library for writing long running processes with a cli interface

[![Build Status](https://travis-ci.org/walkr/oi.svg?branch=master)](https://travis-ci.org/walkr/oi)


### Usage

####1. Create new project

```shell
$ mkdir program
$ cd program
$ oi init
```


####2. Write your long running program

```python
# programd.py

import oi

program = oi.Program('my program', 'ipc:///tmp/program.sock')
program.add_command('ping', lambda p: 'pong')
program.add_command('state', lambda p: p.state)
program.run()  # program will run forever
```

####3. Add a ctl interface

```python
# programctl.py

import oi

ctl = oi.CtlProgram('ctl program', address='ipc:///tmp/program.sock')
ctl.run()
```

####4. Install

```shell
$ python setup.py install
```

####5. Run program, then check ctl
```shell
$ programd --config /etc/program.conf

$ programctl  # enter ctl loop
programctl > ping
pong

$ programctl ping # OR ping end exit
```

#### Also, check out the makefile
```shell
# Help
$ make help

# Upload your program to pypi
$ make distribute
```

### Now the interesting bit. Are you ready?
Run your program on one computer, then control it from another with a single line change (actually two).

Just change the address `ipc:///tmp/program.sock` to a tcp address, such as `tcp://192.168.1.100:5000` in both your `programd.py` and `programctl.py`. That's it! (:


#### License

MIT License
