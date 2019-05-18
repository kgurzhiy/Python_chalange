import random
import types


class InvalidArgumentValueError(Exception):
    my_message = 'Invalid generator argument value'


class IncorrectArgumentTypeError(Exception):
    my_message = 'Incorrect generator argument type'


class BaseIterator:

    __slots__ = ('items', 'cursor')

    def __init__(self, items):
        self.items = items
        self.cursor = -1

    def __iter__(self):
        self._valid_items_type()
        return self

    def _valid_items_type(self):
        raise NotImplementedError

    @staticmethod
    def __valid_args(*args):
        if all(isinstance(x, int) and not isinstance(x, bool) for x in args):
            first_value, last_value, step = args
            if (
                    first_value < last_value and step < 0
            ) or (
                    (first_value > last_value) and step > 0
            ) or step == 0:
                raise InvalidArgumentValueError(
                    'Invalid generator argument value'
                )
        else:
            raise IncorrectArgumentTypeError(
                'Incorrect generator argument type'
            )

    def range_generator(self, start, end, step=1):
        if not self.__valid_args(start, end, step):
            num = start
            while num < end + 1 if end > start else num > end - 1:
                yield num
                num += step

    def __repr__(self):
        return f'{self.__class__.__name__}({self.items})'


class ListIterator(BaseIterator):
    __slots__ = ()

    def _valid_items_type(self):
        if isinstance(self.items, list) and self.items != []:
            return True

    def __next__(self):
        if self.cursor + 1 >= len(self.items):
            raise StopIteration
        self.cursor += 1
        return self.items[self.cursor]

    def __getitem__(self, key):
        self._valid_items_type()
        return self.items[key]


class TupleIterator(ListIterator):
    __slots__ = ()

    def _valid_items_type(self):
        if isinstance(self.items, tuple) and self.items != ():
            return True


class SetIterator(BaseIterator):
    __slots__ = ()

    def _valid_items_type(self):
        if isinstance(self.items, set) and self.items != set():
            return True

    def __next__(self):
        if len(self.items) == 0:
            raise StopIteration
        return self.items.pop()


TEST_TYPE_DATA = [
        random.sample(range(1, 7), 6),
        tuple(random.sample(range(-7, 7), 6)),
        set(random.sample(range(10, 17), 3)),
        str(random.randint(-10000000000, 10000000)),
        random.uniform(-1000000000.0, 100000000000.0),
        {1: 11, 2: 22, 3: 33},
        lambda x: x + 2,
        '', [], {}, (), set(), True, False, None,
        random.randint(-10000, 100000)
]


def test_set_iterator():
    for i in range(100):
        set_arg = set(random.sample(range(-100, 100), 10))
        test_list = list(set_arg)
        set_item = SetIterator(set_arg)
        assert [z for z in set_item] == list(test_list), (
            'SetIter class is not iterator'
        )
        assert [z for z in set_item] == [], 'Tested set wasnt iterated'

        test_start = random.randint(-1000, 0)
        test_end = random.randint(1, 1000)
        test_step = random.randint(1, 100)
        assert (
            isinstance(
                (set_item.range_generator(test_start, test_end, test_step)),
                types.GeneratorType
            ) ==
            isinstance(
                (x for x in range(test_start, test_end, test_step)),
                types.GeneratorType
            )
        ), 'Generator object test failed'

    test_type_data = [
        random.sample(range(1, 7), 6),
        tuple(random.sample(range(-7, 7), 6)),
        str(random.randint(-10000000000, 10000000)),
        random.uniform(-1000000000.0, 100000000000.0),
        {1: 11, 2: 22, 3: 33},
        lambda x: x + 2,
        '', [], {}, (), set(), True, False, None,
        random.randint(-10000, 100000)
    ]
    for i in test_type_data:
        try:
            test_items = SetIterator(i)
            return [x for x in test_items]
        except Exception as e:
            assert isinstance(
                e, StopIteration
            ), 'Invalid items type test failed'

    try:
        test_generator = SetIterator(1)
        return [x for x in test_generator.range_generator(1, 2, 0)]
    except Exception as e:
            assert isinstance(
                e,
                InvalidArgumentValueError
            ), 'Invalid generator argument value'


def test_list_iterator():
    for i in range(100):
        list_arg = random.sample(range(-100, 100), 10)
        test_list = list_arg
        list_item = ListIterator(list_arg)
        assert [z for z in list_item] == test_list, (
            'ListIter class is not iterator'
        )
        assert [z for z in list_item] == [], 'Tested list wasnt iterated'

        test_start = random.randint(-1000, 0)
        test_end = random.randint(1, 1000)
        test_step = random.randint(1, 100)
        assert (
            isinstance(
                (list_item.range_generator(test_start, test_end, test_step)),
                types.GeneratorType
            ) ==
            isinstance(
                (x for x in range(test_start, test_end, test_step)),
                types.GeneratorType
            )
        ), 'Generator object test failed'

    for i in TEST_TYPE_DATA[1:]:
        try:
            test_items = ListIterator(i)
            return [x for x in test_items]
        except Exception as e:
            assert isinstance(e, StopIteration), 'Invalid type test failed'

    for i in TEST_TYPE_DATA[:-1]:
        try:
            test_generator = ListIterator(1)
            print([x for x in test_generator.range_generator(i, 6)])
        except Exception as e:
            assert isinstance(
                e,
                IncorrectArgumentTypeError
            ), 'Invalid generator argument type'

    test_index = ListIterator([[10], 9, 8, 7])
    assert test_index[0] == [10], 'Indexing fail'


def test_tuple_iterator():
    for i in range(100):
        tuple_arg = random.sample(range(-100, 100), 10)
        test_list = tuple_arg
        tuple_item = TupleIterator(tuple(tuple_arg))
        assert [z for z in tuple_item] == test_list, (
            'TupleIter class is not iterator'
        )
        assert [z for z in tuple_item] == [], 'Tested tuple wasnt iterated'

        test_start = random.randint(-1000, 0)
        test_end = random.randint(1, 1000)
        test_step = random.randint(1, 100)
        assert (
            isinstance(
                (tuple_item.range_generator(test_start, test_end, test_step)),
                types.GeneratorType
            ) ==
            isinstance(
                (x for x in range(test_start, test_end, test_step)),
                types.GeneratorType
            )
        ), 'Generator object test failed'

    test_tuple_data = [
        random.sample(range(1, 7), 6),
        set(random.sample(range(10, 17), 3)),
        str(random.randint(-10000000000, 10000000)),
        random.uniform(-1000000000.0, 100000000000.0),
        {1: 11, 2: 22, 3: 33},
        lambda x: x + 2,
        '', [], {}, (), set(), True, False, None,
        random.randint(-10000, 100000)
    ]
    for i in test_tuple_data:
        try:
            test_items = TupleIterator(i)
            return [x for x in test_items]
        except Exception as e:
            assert isinstance(e, StopIteration), 'Invalid type test failed'

    for i in TEST_TYPE_DATA[:-1]:
        try:
            test_generator = TupleIterator(1)
            print([x for x in test_generator.range_generator(i, 6)])
        except Exception as e:
            assert isinstance(
                e,
                IncorrectArgumentTypeError
            ), 'Invalid generator argument type'

    test_index = TupleIterator(([10], 9, 8, 7))
    assert test_index[3] == 7, 'Indexing fail'


if __name__ == '__main__':
    test_set_iterator()
    test_list_iterator()
    test_tuple_iterator()
