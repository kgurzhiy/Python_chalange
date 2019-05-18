import random


class IncorrectDecoratorArgument(Exception):
    my_message = 'Incorrect decorator argument'


def repeat_decorator(argument):
    def wrapped(func_result):
        def inner(*args, **kwargs):
            result_list = []
            if not isinstance(argument, int) or (argument < 1):
                raise IncorrectDecoratorArgument
            for i in range(argument):
                result_list.append(func_result(*args, **kwargs))
            return result_list
        return inner
    return wrapped


def test_repeat_decorator():
    invalid_args = [
        random.randint(-1000000000000000, 0),
        str(random.randint(-1000000000000, 1000000000)),
        random.uniform(-100000000000.0, 100000000000000.0),
        random.sample(range(1, 7), 6),
        tuple(random.sample(range(-7, 7), 6)),
        set(random.sample(range(10, 17), 3)),
        {1: 11, 2: 22, 3: 33},
        lambda x: x + 2,
        '', [], {}, (), False, True, None
    ]
    random_arg = random.randint(1, 5)
    for i in invalid_args:
        try:
            @repeat_decorator(i)
            def test_decorator_argument():
                return 1
            test_decorator_argument()
        except Exception as e:
            assert isinstance(e, IncorrectDecoratorArgument), 'invalid arg'

    @repeat_decorator(random_arg)
    def test_positive(x):
        return x/x

    @repeat_decorator(random_arg)
    def test_positive_print():
        print('i love Python')

    test_positive_print_list = []
    test_positive_list = []
    for i in range(random_arg):
        test_positive_list.append(1)
        test_positive_print_list.append('I like python')
    assert test_positive(random_arg) == test_positive_list
    assert test_positive_print() == test_positive_print_list
