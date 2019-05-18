import random


class InvalidArgumentValueError(Exception):
    my_message = 'Invalid generator argument value'


class IncorrectArgumentTypeError(Exception):
    my_message = 'Incorrect generator argument type'


class SearchMaxPrime:

    __slots__ = ('first_value', 'last_value', 'step', 'generated_range')

    def __init__(self, first_value, last_value, step=1):
        self.__args_validation(first_value, last_value, step)
        self.first_value = first_value
        self.last_value = last_value
        self.step = step
        self.generated_range = None

    def __repr__(self):
        return (
            f'{self.__class__.__name__}({self.first_value}, '
            f'{self.last_value}, {self.step})'
        )

    @staticmethod
    def __args_validation(*args):
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

    @staticmethod
    def __generate_range(start, end, increment):
        range_list = []
        k = start
        if start > end:
            while k > (end - 1):
                range_list.append(k)
                k += increment
        elif start < end:
            while k < (end + 1):
                range_list.append(k)
                k += increment
        else:
            range_list.append(start)
        return range_list

    def __sieve_of_eratosthenes(self):
        """
        The optimal algorithm for generating prime numbers.
        """
        if self.last_value > 1:
            range_list = self.__generate_range(0, self.last_value, 1)
            sieve_list = []
            i = 2
            while i <= self.last_value:
                if range_list[i] != 0:
                    sieve_list.append(range_list[i])
                    for j in self.__generate_range(i, self.last_value, i):
                        range_list[j] = 0
                i += 1
            return sieve_list
        else:
            return ()

    def get_generated_range(self):
        if self.generated_range:
            return self.generated_range
        self.generated_range = self.__generate_range(
            self.first_value,
            self.last_value,
            self.step
        )
        return self.generated_range

    def get_max_prime(self):
        common_values = tuple(
            set(self.__sieve_of_eratosthenes()) &
            set(self.get_generated_range())
        )
        if common_values == ():
            return None
        else:
            return max(common_values)


def test_get_generated_range_positive():
    for i in range(100):
        min_value = random.randint(-10000, -100)
        max_value = random.randint(-100, 0)
        random_step = random.randint(1, 10)
        test_range = SearchMaxPrime(min_value, max_value, random_step)
        assert test_range.get_generated_range() == list(
            range(min_value, max_value+1, random_step)
        ), 'start < 0, end < 0'
    for i in range(100):
        min_value = random.randint(100, 1000)
        max_value = random.randint(-10000, 99)
        random_step = random.randint(-10, -1)
        test_range = SearchMaxPrime(min_value, max_value, random_step)
        assert test_range.get_generated_range() == list(
            range(min_value, max_value - 1, random_step)
        ), 'start < end '
    for i in range(100):
        min_value = random.randint(0, 100)
        max_value = random.randint(101, 100000)
        random_step = random.randint(1, 10)
        test_range = SearchMaxPrime(min_value, max_value, random_step)
        assert test_range.get_generated_range() == list(
            range(min_value, max_value + 1, random_step)
        ), 'start > end '
    for i in range(100):
        min_value = random.randint(-1000, 1000)
        max_value = random.randint(1001, 100000)
        test_range = SearchMaxPrime(min_value, max_value)
        assert test_range.get_generated_range() == list(
            range(min_value, max_value + 1)
        ), 'no step'
    for i in range(100):
        value = random.randint(-1000, 1000)
        test_range = SearchMaxPrime(value, value)
        assert test_range.get_generated_range() == list(
            range(value, value + 1)
        ), 'start == end'


def test_get_max_prime_positive():
    for i in range(100):
        min_value = random.randint(-10000, -100)
        max_value = random.randint(-99, 0)
        random_step = random.randint(1, 10)
        test_range = SearchMaxPrime(min_value, max_value, random_step)
        assert test_range.get_max_prime() is None, 'no prime numbers in range'
    for i in range(100):
        min_value = random.randint(-100, 100)
        test_range = SearchMaxPrime(min_value, 113)
        assert test_range.get_max_prime() == 113, 'failed to find max'
    test_range_1 = SearchMaxPrime(4, 100, 4)
    assert test_range_1.get_max_prime() is None, 'no prime numbers in range'
    test_range_2 = SearchMaxPrime(1, 1, 1)
    assert test_range_2.get_max_prime() is None, 'no prime numbers in range'
    test_range_3 = SearchMaxPrime(103, 109, 4)
    assert test_range_3.get_max_prime() == 107, 'failed to find max'


def test_get_max_prime_type():
    random_value = [
        str(random.randint(-1000000000000, 1000000000)),
        random.uniform(-100000000000.0, 100000000000000.0),
        random.sample(range(1, 7), 6),
        tuple(random.sample(range(-7, 7), 6)),
        set(random.sample(range(10, 17), 3)),
        {1: 11, 2: 22, 3: 33},
        lambda x: x + 2,
        '', [], {}, (), False, True, None
    ]
    try:
        for tested_arg in random_value:
            test_range = SearchMaxPrime(random.randint(0, 100), tested_arg)
            return test_range.get_max_prime()
    except BaseException as e:
        assert isinstance(e, IncorrectArgumentTypeError), (
            'incorrect type of arg'
        )


def test_get_max_prime_step():
    try:
        for i in range(100):
            min_value = random.randint(-1000, 1000)
            max_value = random.randint(-1000, 1000)
            test_range = SearchMaxPrime(min_value, max_value, 0)
            return test_range.get_max_prime()
    except BaseException as e:
        assert isinstance(e, InvalidArgumentValueError), 'step == 0'


def test_get_max_prime_sign():
    try:
        for i in range(100):
            min_value = random.randint(100, 1000)
            max_value = random.randint(-1000, 99)
            random_step = random.randint(1, 10)
            test_range = SearchMaxPrime(min_value, max_value, random_step)
            return test_range.get_max_prime()
    except BaseException as e:
        assert isinstance(e, InvalidArgumentValueError), (
            'icorrect args for get_max_prime'
        )


if __name__ == '__main__':
    test_get_generated_range_positive()
    test_get_max_prime_positive()
    test_get_max_prime_type()
    test_get_max_prime_step()
    test_get_max_prime_sign()
