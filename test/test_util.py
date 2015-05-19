from oi import util


def test_qsplit():
    tests = [
        ('one', ['one']),
        (' one ', ['one']),
        (' " one " ', ['one']),
        ('one two', ['one', 'two']),
        ('one   two', ['one', 'two']),
        ('one "two three" four', ['one', 'two three', 'four']),
        ('1 2 "3 4" 5 6 "7 8"', ['1', '2', '3 4', '5', '6', '7 8'])
    ]

    def check(a, b):
        assert a == b

    for text, expected in tests:
        yield check, util.split(text), expected
