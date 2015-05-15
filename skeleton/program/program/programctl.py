import oi


def main():
    ctl = oi.CtlProgram('ctl program', 'ipc:///tmp/oi-random_string.sock')
    ctl.run()


if __name__ == '__main__':
    main()
