oi
==
python library for writing long running processes with a cli interface



## Usage

####1. Create new project

```shell
$ mkdir program
$ cd program
$ oi init
```


####2. Write your long running program

```python
# program.py

import oi

program = oi.Program('My sweet program', address='ipc:///tmp/myprogram.sock')
program.run()  # program will run forever
```

####3. Add a ctl interface

```python
# programctl

import oi

ctl = oi.CtlProgram('ctl for my program', address='ipc:///tmp/myprogram.sock')
ctl.run()
```

####4. Install

```shell
$ python setup.py install
```

####5. Run program, then check ctl
```shell
$ programd --config /etc/programd.conf

$ programctl  # enter ctl loop
programctl > ping
pong

$ programctl ping # OR ping end exit
```

#### Also, check out the makefile
```shell
# Help
$ make help

# Upload to pypi
$ make distribute
```

## Now the interesting bit. Are you ready?
Run your program on one computer, then control from anywhere with a single line change (actually two).

Just change the address `ipc:///tmp/program.sock` to a real `tcp://192.168.1.100:5000` in both your `programd` and `programctl`. That's it! (:


#### License

MIT License
