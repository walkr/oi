try:
    input = raw_input
except NameError:
    input = input

try:
    import configparser
except ImportError:
    import ConfigParsers as configparser
