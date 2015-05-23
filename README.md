oi
==
python library for writing long running processes with a cli interface

[![Build Status](https://travis-ci.org/walkr/oi.svg?branch=master)](https://travis-ci.org/walkr/oi)

![oi image](http://i.imgur.com/iH08GNq.png)


### Install

Note: You need [nanomsg](https://github.com/nanomsg/nanomsg) installed on your system:

```shell
$ git clone git@github.com:nanomsg/nanomsg.git
$ cd nanomsg
$ ./configure
$ make
$ make check
$ sudo make install
```

Then install oi

```shell
$ pip install oi
```

### Usage


####1. Write your long running program

```python
# programd.py

import oi

program = oi.Program('my program', 'ipc:///tmp/program.sock')
program.add_command('ping', lambda: 'pong')
program.add_command('state', lambda: program.state)
program.run()  # program will run forever
```

####2. Add a ctl interface

```python
# programctl.py

import oi

ctl = oi.CtlProgram('ctl program', address='ipc:///tmp/program.sock')
ctl.run()
```


####3. Run program, then connect to it via ctl
```shell
# Run process
$ python programd

# OR with a configuration file
$ python programd --config /etc/program.conf

$ python programctl  # enter ctl loop
programctl > ping
pong

# OR ping end exit
$ python programctl ping
```

#### Quickly get started with a new project

```shell
$ mkdir xprogram
$ cd xprogram

$ oi init
$ make install

# Start your program
$ xprogramd

# Start ctl program
$ xprogramctl
ctl > ping
pong

# Upload to pypi (Edit setup.py before distributing)
$ make distribute
```

### Now the interesting bit. Are you ready?
Run your program on one computer, then control it from another with a single line change (actually two).

Just change the address `ipc:///tmp/program.sock` to a tcp address, such as `tcp://192.168.1.100:5000` in both your `programd.py` and `programctl.py`. That's it! (:

#### TODO

- [ ] Add more testing

#### License

MIT License
