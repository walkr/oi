try:
    input = raw_input
except NameError:
    input = input

try:
    import configparser
except ImportError:
    import ConfigParser as configparser
