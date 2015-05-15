import oi


def main():
    ctl = oi.CtlProgram('ctl program', 'ipc:///tmp/programd.sock')
    ctl.run()

if __name__ == '__main__':
    main()
