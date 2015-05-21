import sys
import oi


def main():
    addr = sys.argv.pop(1)
    print('addr is: `{}`'.format(addr))
    ctl = oi.CtlProgram('ctl program', addr)
    ctl.run()

if __name__ == '__main__':
    main()
