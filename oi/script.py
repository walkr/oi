from . import core


def create_new_project():
    print('Creating new program')


def main():
    oi = core.CtlProgram(
        'init a new oi program in current empty directory', None)
    oi.parser.add_argument('init', help='initialize new oi project')
    oi.runner.add('init', create_new_project())
    oi.run(loop=False)


if __name__ == '__main__':
    main()
