import json
import os.path
import random
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom


class InvalidClassParameter(Exception):
    error_massage = 'Invalid maximum sequence len parameter'


class IncorrectArgumentTypeError(Exception):
    error_massage = 'Incorrect generator argument type'


class InvalidArgumentValueError(Exception):
    error_massage = 'Invalid generator argument value'


class InvalidSequenceLen(Exception):
    error_massage = 'Sequence length is greater than a given value'


class BadSeqType(Exception):
    error_massage = 'Invalid seq type'


class InvalidJson(Exception):
    error_massage = 'Invalid json file'


class InvalidXML(Exception):
    error_message = 'Invalid xml file'


class InvalidFileTypeArgument(Exception):
    error_massage = 'File type argument should be Json or XML'


class InappropriateTypeForFiboGeneration(Exception):
    error_massage = (
        'The sequence with given arguments'
        ' will not be a fibonacci sequence'
    )


PATH_JSON = 'data.json'
PATH_XML = 'data.xml'
DATE_STAMP = '%d-%m-%Y %H:%M'


class BaseSequenceGenerator:
    __slots__ = (
        'max_sequence', 'sequence', 'element_type', 'appropriate_seq_type',
        'loaded_data', 'meta_arg_1', 'meta_arg_2', 'meta_arg_3', 'max', 'min',
        'meta_arg_4', 'seq_from_file', 'generator_name', 'len', 'seq_type'
    )

    def __init__(self, max_sequence=100):
        self.__valid_max_sequence_arg(max_sequence)
        self.max_sequence = max_sequence
        self.sequence = None
        self.element_type = None
        self.max = None,
        self.min = None,
        self.len = None
        self.appropriate_seq_type = None
        self.loaded_data = None
        self.meta_arg_1 = None
        self.meta_arg_2 = None
        self.meta_arg_3 = None
        self.meta_arg_4 = None
        self.seq_from_file = None
        self.seq_type = 'list'
        self.generator_name = 'range_generator'

    @staticmethod
    def __valid_max_sequence_arg(max_sequence):
        if not isinstance(
                max_sequence,
                int
        ) or isinstance(max_sequence, bool) or (max_sequence < 1):
            raise InvalidClassParameter(
                'Invalid maximum sequence len parameter'
            )

    @staticmethod
    def _invalid_args(*args, generator_type):
        if all(isinstance(x, int) and not isinstance(x, bool) for x in args):
            if generator_type == 'range':
                start, end, step = args
                if (start >= end) or (step <= 0):
                    raise InvalidArgumentValueError(
                        'Invalid generator argument value'
                    )
            elif generator_type == 'fibonacci':
                fib_end = args
                if fib_end[0] <= 1:
                    raise InvalidArgumentValueError(
                        'Invalid generator argument value'
                    )
        else:
            raise IncorrectArgumentTypeError(
                'Incorrect generator argument type'
            )

    def _valid_sequence_len(self, sequence):
        if len(sequence) > self.max_sequence:
            raise InvalidSequenceLen(
                'Sequence length is greater than a given value'
            )

    def _range_generator(self, start, end, step=1):
        if not self._invalid_args(start, end, step, generator_type='range'):
            num = start
            while num < end:
                yield num
                num += step

    @staticmethod
    def _invalid_fibonacci_pair(fibonacci_pair):
        if not isinstance(fibonacci_pair, tuple) or not len(
            fibonacci_pair
        ) == 2 or not (
            isinstance(fibonacci_pair[0], int) and not isinstance(
                fibonacci_pair[0], bool
            ) and isinstance(fibonacci_pair[1], int) and not isinstance(
                fibonacci_pair[1], bool
            )
        ):
            raise IncorrectArgumentTypeError(
                'Incorrect generator argument type'
            )

    def _fibonacci_generator(self, fibonacci_pair, fib_index):
        self.generator_name = 'fibonacci_generator'
        if not self._invalid_fibonacci_pair(
                fibonacci_pair
        ) and not self._invalid_args(fib_index, generator_type='fibonacci'):
            fib_1, fib_2 = fibonacci_pair[0], fibonacci_pair[1]
            self.min = fib_1
            self.element_type = fib_1
            for _ in self._range_generator(0, fib_index):
                self.max = fib_1
                yield fib_1
                fib_1, fib_2 = fib_2, fib_1 + fib_2

    def _data_to_write(self, file_path):
        date_created = datetime.fromtimestamp(
            os.path.getctime(file_path)
        ).strftime(DATE_STAMP)
        date_modified = datetime.fromtimestamp(
            os.path.getmtime(file_path)
        ).strftime(DATE_STAMP)
        if isinstance(self.sequence, set):
            self.sequence = tuple(self.sequence)
        file_data = {
            'sequence': self.sequence,
            'meta': {
                'generator_name': self.generator_name,
                'seq_type': self.seq_type,
                'seq_len': self.len,
                'el_type': type(self.element_type).__name__,
                'date_created': date_created,
                'date_modified': date_modified,
                'author': self.__class__.__name__,
                'min_element': self.min,
                'max_element': self.max
            }
        }
        return file_data

    def _serialise_xml_data(self):
        generated_data = ET.Element('generated_data')
        for main_key in self._range_generator(
                0,
                len(self._data_to_write(PATH_XML).keys())
        ):
            sub_name = ET.SubElement(
                generated_data,
                f'{list(self._data_to_write(PATH_XML).keys())[main_key]}'
            )
            sub_name.text = None

        for seq_elem in self._range_generator(0, len(self.sequence)):
            if self._data_to_write(PATH_XML)['meta']['seq_type'] == 'dict':
                elem = ET.SubElement(
                    generated_data[0], 'elem',
                    id=str(tuple(self.sequence.keys())[seq_elem])
                )
                elem.text = str(tuple(self.sequence.values())[seq_elem])
            else:
                elem = ET.SubElement(generated_data[0], 'elem')
                elem.text = str(self.sequence[seq_elem])
        for i in self._range_generator(
                0,
                len(self._data_to_write(PATH_XML)['meta'].keys())
        ):
            sub_meta = ET.SubElement(
                generated_data[1],
                f"{list(self._data_to_write(PATH_XML)['meta'].keys())[i]}"
            )
            sub_meta.text = str(
                list(self._data_to_write(PATH_XML)['meta'].values())[i]
            )
        xml_str = minidom.parseString(
            ET.tostring(generated_data)
        ).toprettyxml(indent="    ")
        return xml_str

    def _valid_file(self, file_to_create, file):
        try:
            if file_to_create == PATH_JSON:
                self.loaded_data = json.load(file)
            elif file_to_create == PATH_XML:
                self.loaded_data = ET.parse(file)
            return self.loaded_data
        except (ValueError, ET.ParseError):
            return False

    def _write_data(self, file_to_create, file):
        file.seek(0)
        file.truncate()
        if file_to_create == PATH_JSON:
            return json.dump(self._data_to_write(PATH_JSON), file, indent=2)
        elif file_to_create == PATH_XML:
            return file.write(self._serialise_xml_data())

    def _overwrite_metadata_only(self, file_to_create, file):
        file.seek(0)
        file.truncate()
        if file_to_create == PATH_JSON:
            self.loaded_data['meta'] = self._data_to_write(
                file_to_create
            )['meta']
            return json.dump(self.loaded_data, file, indent=2)
        elif file_to_create == PATH_XML:
            root = self.loaded_data.getroot()
            value_tuple = tuple(
                self._data_to_write(file_to_create)['meta'].values()
            )
            for i in self._range_generator(0, len(value_tuple)):
                root[1][i].text = str(value_tuple[i])
            return self.loaded_data.write(file_to_create)

    def _is_need_to_generate_new_info(
            self, file_to_create, first_arg, second_arg, third_arg, fourth_arg
    ):
        if file_to_create == PATH_XML:
            meta_info = self.loaded_data.findall('meta')
            path_tuple = (first_arg, second_arg, third_arg, fourth_arg)
            value_list = []
            for info in meta_info:
                for path in path_tuple:
                    meta_keys = info.findall(path)
                    for val in meta_keys:
                        value_list.append(val.text)
            if len(value_list) == 4:
                self.meta_arg_1 = ''.join(value_list[0])
                self.meta_arg_2 = ''.join(value_list[1])
                self.meta_arg_3 = ''.join(value_list[2])
                self.meta_arg_4 = ''.join(value_list[3])
        elif file_to_create == PATH_JSON:
            self.meta_arg_1 = self.loaded_data.get('meta').get(first_arg)
            self.meta_arg_2 = self.loaded_data.get('meta').get(second_arg)
            self.meta_arg_3 = self.loaded_data.get('meta').get(third_arg)
            self.meta_arg_4 = self.loaded_data.get('meta').get(fourth_arg)
        if (
            str(self.meta_arg_1) != str(
                self._data_to_write(file_to_create)['meta'][first_arg]
            )
        ) or (
            str(self.meta_arg_2) != str(
                self._data_to_write(file_to_create)['meta'][second_arg]
            )
        ) or (
            self.meta_arg_3 != self._data_to_write(
                file_to_create
            )['meta'][third_arg]
        ) or (
            self.meta_arg_4 != self._data_to_write(
                file_to_create
            )['meta'][fourth_arg]
        ):
            return True

    def _generate_sequence(self, file_type):
        if file_type == 'json':
            file_to_create = PATH_JSON
            file_to_delete = PATH_XML
        elif file_type == 'xml':
            file_to_create = PATH_XML
            file_to_delete = PATH_JSON
        else:
            raise InvalidFileTypeArgument(
                'File type argument should be Json or XML'
            )
        if os.path.isfile(file_to_delete):
            os.remove(file_to_delete)
        if os.path.isfile(file_to_create) and os.path.getsize(
                file_to_create
        ) > 0:
            file_mode = 'r+'
        else:
            file_mode = 'w'
        if self.max_sequence < len(self.sequence):
            raise InvalidSequenceLen(
                'Sequence length is greater than a given value'
            )
        with open(file_to_create, file_mode) as file:
            if file_mode == 'r+':
                if not self._valid_file(file_to_create, file):
                    self._write_data(file_to_create, file)
                else:
                    if self._is_need_to_generate_new_info(
                            file_to_create, 'seq_type', 'author',
                            'min_element', 'max_element'
                    ):
                        if not self._is_need_to_generate_new_info(
                                file_to_create, 'generator_name',
                                'seq_len', 'min_element', 'max_element'
                        ):
                            self._overwrite_metadata_only(file_to_create, file)
                        else:
                            self._write_data(file_to_create, file)
                    else:
                        pass
            else:
                self._write_data(file_to_create, file)

    def __get_sequence_from_xml(self):
        meta_info = self.loaded_data.findall('meta')
        path_tuple = ('generator_name', 'seq_type')
        value_list = []
        for info in meta_info:
            for path in path_tuple:
                meta_keys = info.findall(path)
                for val in meta_keys:
                    value_list.append(val.text)

        if len(value_list) != 2:
            raise InvalidXML('Invalid xml file')
        self.generator_name = ''.join(value_list[0])
        self.seq_type = ''.join(value_list[1])
        sequence = self.loaded_data.findall('sequence')
        self.seq_from_file = []
        for element in sequence:
            seq_elem = element.findall('elem')
            for i in seq_elem:
                self.seq_from_file.append(i.text)
        if self.seq_type == 'dict':
            self.seq_from_file = {
                    str(i): i for i in list(map(int, self.seq_from_file))
            }
        elif self.seq_type in ('list', 'tuple', 'set'):
            self.seq_from_file = list(map(int, self.seq_from_file))
        else:
            raise InvalidXML('Invalid xml file')
        return self.seq_from_file

    def __get_sequence_from_json(self):
        self.seq_type = self.loaded_data.get('meta').get('seq_type')
        self.generator_name = self.loaded_data.get('meta').get(
            'generator_name'
        )
        if self.seq_type is None:
            raise InvalidJson('Invalid json file')
        self.seq_from_file = self.loaded_data.get('sequence')
        return self.seq_from_file

    def _get_sequence(self):
        if os.path.isfile(PATH_XML) and not os.path.isfile(PATH_JSON):
            file_path = PATH_XML
        elif os.path.isfile(PATH_JSON) and not os.path.isfile(PATH_XML):
            file_path = PATH_JSON
        else:
            if self.appropriate_seq_type == 'dict':
                return {}
            else:
                return []
        with open(file_path, 'r') as file:
            if not self._valid_file(file_path, file):
                raise (InvalidXML(
                    'Invalid xml file'
                ) if file_path == PATH_XML else InvalidJson(
                    'Invalid json file')
                       )
            if file_path == PATH_XML:
                self.seq_from_file = self.__get_sequence_from_xml()
            elif file_path == PATH_JSON:
                self.seq_from_file = self.__get_sequence_from_json()
            if (
                self.seq_type == 'dict' and self.appropriate_seq_type != 'dict'
            ) or (
                self.seq_type != 'dict' and self.appropriate_seq_type == 'dict'
            ):
                raise BadSeqType('Invalid seq type')
            if self.max_sequence < len(self.seq_from_file):
                raise InvalidSequenceLen(
                    'Sequence length is greater than a given value'
                )
            if (
                self.__class__.__name__ in (
                    'DictSequenceGenerator', 'SetSequenceGenerator'
                ) and self.generator_name == 'fibonacci_generator'
            ):
                raise InappropriateTypeForFiboGeneration(
                    'The sequence with given arguments'
                    ' will not be a fibonacci sequence'
                )
        return self.seq_from_file

    def _additional_range_generator(self, start, end, step=1):
        if not self._invalid_args(start, end, step, generator_type='range'):
            self.min = start
            self.len = 0
            num = start
            while num < end:
                self.max = num
                yield num
                num += step
                self.len += 1

    def __repr__(self):
        return f'{self.__class__.__name__}({self.max_sequence})'


class ListSequenceGenerator(BaseSequenceGenerator):
    __slots__ = ()

    def generate_range_sequence(self, file_type, start, end, step=1):
        self.sequence = [
            i for i in self._additional_range_generator(start, end, step)
        ]
        self.element_type = start
        return self._generate_sequence(file_type)

    def generate_fibonacci_sequence(self, file_type, fibonacci_pair, fib_len):
        self.sequence = [
            i for i in self._fibonacci_generator(fibonacci_pair, fib_len)
        ]
        self.len = fib_len
        return self._generate_sequence(file_type)

    def get_sequence(self):
        self.appropriate_seq_type = 'list'
        return self._get_sequence()


class TupleSequenceGenerator(ListSequenceGenerator):
    __slots__ = ()

    def generate_range_sequence(self, file_type, start, end, step=1):
        self.seq_type = 'tuple'
        return super().generate_range_sequence(file_type, start, end, step)

    def generate_fibonacci_sequence(self, file_type, fibonacci_pair, fib_len):
        self.seq_type = 'tuple'
        return super().generate_fibonacci_sequence(
            file_type, fibonacci_pair, fib_len
        )

    def get_sequence(self):
        self.appropriate_seq_type = 'tuple'
        return tuple(self._get_sequence())


class SetSequenceGenerator(ListSequenceGenerator):
    __slots__ = ()

    def generate_range_sequence(self, file_type, start, end, step=1):
        self.seq_type = 'set'
        return super().generate_range_sequence(file_type, start, end, step)

    def generate_fibonacci_sequence(self, file_type, fibonacci_pair, fib_len):
        if fibonacci_pair[0] == fibonacci_pair[1]:
            raise InappropriateTypeForFiboGeneration(
                'The sequence with given arguments'
                ' will not be a fibonacci sequence'
            )
        self.seq_type = 'set'
        return super().generate_fibonacci_sequence(
            file_type, fibonacci_pair, fib_len
        )

    def get_sequence(self):
        self.appropriate_seq_type = 'set'
        return set(self._get_sequence())


class DictSequenceGenerator(BaseSequenceGenerator):
    __slots__ = ()

    def generate_range_sequence(self, file_type, start, end, step=1):
        self.sequence = {
                z: z for z in self._additional_range_generator(start, end, step)
            }
        self.min = str(self.min)
        self.max = str(self.max)
        self.element_type = {start: start}.values()
        self.seq_type = 'dict'
        return self._generate_sequence(file_type)

    def generate_fibonacci_sequence(self, file_type, fibonacci_pair, fib_len):
        if fibonacci_pair[0] == fibonacci_pair[1]:
            raise InappropriateTypeForFiboGeneration(
                'The sequence with given arguments'
                ' will not be a fibonacci sequence'
            )
        self.sequence = {
            z: z for z in self._fibonacci_generator(fibonacci_pair, fib_len)
        }
        self.element_type = {fibonacci_pair[0]: fibonacci_pair[0]}.values()
        self.min = str(fibonacci_pair[0])
        self.max = str(self.max)
        self.len = fib_len
        self.seq_type = 'dict'
        return self._generate_sequence(file_type)

    def get_sequence(self):
        self.appropriate_seq_type = 'dict'
        return self._get_sequence()


def test_meta_data(*args):
    test_generator_name = None
    test_seq_type = None
    test_seq_len = None
    test_el_type = None
    test_author = None
    test_min_element = None
    test_max_element = None
    author = None
    element_type = None
    if len(args) == 5:
        file_type, rand_start, rand_end, rand_step, seq_type = args
        if file_type == 'xml':
            with open(PATH_XML, 'r') as file:
                loaded_data = ET.parse(file)
                meta_info = loaded_data.findall('meta')
                path_tuple = (
                    'generator_name', 'seq_type', 'seq_len', 'el_type',
                    'date_created', 'date_modified', 'author',
                    'min_element', 'max_element'
                )
                value_list = []
                for info in meta_info:
                    for path in path_tuple:
                        meta_keys = info.findall(path)
                        for val in meta_keys:
                            value_list.append(val.text)
                assert len(value_list) == 9, 'invalid number of meta info'
                test_generator_name = ''.join(value_list[0])
                test_seq_type = ''.join(value_list[1])
                test_seq_len = int(''.join(value_list[2]))
                test_el_type = ''.join(value_list[3])
                test_author = ''.join(value_list[6])
                test_min_element = ''.join(value_list[7])
                test_max_element = ''.join(value_list[8])
        elif file_type == 'json':
            with open(PATH_JSON, 'r') as file:
                loaded_data = json.load(file)
                test_generator_name = loaded_data.get('meta').get(
                    'generator_name'
                )
                test_seq_type = str(loaded_data.get('meta').get('seq_type'))
                test_seq_len = loaded_data.get('meta').get('seq_len')
                test_min_element = loaded_data.get('meta').get('min_element')
                test_max_element = loaded_data.get('meta').get('max_element')
                test_el_type = str(loaded_data.get('meta').get('el_type'))
                test_author = loaded_data.get('meta').get('author')
        assert test_generator_name == 'range_generator'
        assert str(test_seq_type) == seq_type, 'Incorrect seq type'
        assert str(test_seq_len) == str(
            len([i for i in range(rand_start, rand_end, rand_step)])
        ), 'len'
        assert str(test_min_element) == str(rand_start), 'min'
        if seq_type != 'dict':
            assert str(test_max_element) == str(
                max([i for i in range(rand_start, rand_end, rand_step)])
            ), 'max'
        else:
            assert str(test_max_element) == str(
                max({x: x for x in range(rand_start, rand_end, rand_step)})
            )
        if seq_type == 'list':
            author = 'ListSequenceGenerator'
            element_type = 'int'
        elif seq_type == 'tuple':
            author = 'TupleSequenceGenerator'
            element_type = 'int'
        elif seq_type == 'set':
            author = 'SetSequenceGenerator'
            element_type = 'int'
        elif seq_type == 'dict':
            author = 'DictSequenceGenerator'
            element_type = 'dict_values'
        assert test_author == author, 'author'
        assert test_el_type == element_type, 'element type'


def test_positive():
    rand_max_value = random.randint(50, 100)
    list_seq = ListSequenceGenerator(rand_max_value)
    tuple_seq = TupleSequenceGenerator()
    dict_seq = DictSequenceGenerator(rand_max_value)
    set_seq = SetSequenceGenerator()
    rand_start = random.randint(-20, 0)
    rand_end = random.randint(1, 20)
    rand_step = random.randint(1, 3)
    file_type = random.choice(['json', 'xml'])

    list_seq.generate_range_sequence(file_type, rand_start, rand_end, rand_step)
    assert os.path.isfile(
        PATH_XML if file_type == 'json' else PATH_JSON
    ) is False, 'Opposite file exists'
    test_meta_data(file_type, rand_start, rand_end, rand_step, 'list')
    assert list_seq.get_sequence() == [
        i for i in range(rand_start, rand_end, rand_step)
    ], 'Generated list sequence is invalid'
    assert tuple_seq.get_sequence() == tuple(
        [i for i in range(rand_start, rand_end, rand_step)]
    ), 'Getting sequence as tuple failed'
    assert set_seq.get_sequence() == {
        i for i in range(rand_start, rand_end, rand_step)
    }, 'Getting sequence as set failed'

    tuple_seq.generate_range_sequence(
        file_type, rand_start, rand_end, rand_step
    )
    assert os.path.isfile(
        PATH_XML if file_type == 'json' else PATH_JSON
    ) is False, 'Opposite file exists'
    test_meta_data(file_type, rand_start, rand_end, rand_step, 'tuple')
    assert list_seq.get_sequence() == [
        i for i in range(rand_start, rand_end, rand_step)
    ], 'Generated tuple sequence is invalid'
    assert tuple_seq.get_sequence() == tuple(
        [i for i in range(rand_start, rand_end, rand_step)]
    ), 'Getting sequence as tuple failed'
    assert set_seq.get_sequence() == {
        i for i in range(rand_start, rand_end, rand_step)
    }, 'Getting sequence as set failed'

    set_seq.generate_range_sequence(file_type, rand_start, rand_end, rand_step)
    assert os.path.isfile(
        PATH_XML if file_type == 'json' else PATH_JSON
    ) is False, 'Opposite file exists'
    test_meta_data(file_type, rand_start, rand_end, rand_step, 'set')
    assert set(list_seq.get_sequence()) == {
        i for i in range(rand_start, rand_end, rand_step)
    }, 'Generated set sequence is invalid'
    assert set(tuple_seq.get_sequence()) == {
        i for i in range(rand_start, rand_end, rand_step)
    }, 'Getting sequence as tuple failed'
    assert set_seq.get_sequence() == {
        i for i in range(rand_start, rand_end, rand_step)
    }, 'Getting sequence as set failed'

    dict_seq.generate_range_sequence(
        file_type, rand_start, rand_end, rand_step
    )

    assert os.path.isfile(
        PATH_XML if file_type == 'json' else PATH_JSON
    ) is False, 'Opposite file exists'
    test_meta_data(file_type, rand_start, rand_end, rand_step, 'dict')
    assert dict_seq.get_sequence() == {
        str(x): x for x in range(rand_start, rand_end, rand_step)
    }, 'Generated dict sequence is invalid'

    list_seq.generate_fibonacci_sequence(file_type, (3, 6), 4)
    assert os.path.isfile(
        PATH_XML if file_type == 'json' else PATH_JSON
    ) is False, 'Opposite file exists'
    assert list_seq.get_sequence() == [
        3, 6, 9, 15
    ], 'Generated list sequence is invalid'
    assert tuple_seq.get_sequence() == (
        3, 6, 9, 15
    ), 'Getting sequence as tuple failed'
    try:
        set_seq.get_sequence()
    except Exception as e:
        assert isinstance(e, InappropriateTypeForFiboGeneration), (
            'InappropriateTypeForFiboGeneration'
        )

    dict_seq.generate_fibonacci_sequence(file_type, (6, 3), 4)
    assert os.path.isfile(
        PATH_XML if file_type == 'json' else PATH_JSON
    ) is False, 'Opposite file exists'
    try:
        dict_seq.get_sequence()
    except Exception as e:
        assert isinstance(e, InappropriateTypeForFiboGeneration), (
            'InappropriateTypeForFiboGeneration'
        )


def test_negative():
    bottom_zero = random.randint(-1, 0)
    try:
        list_seq = ListSequenceGenerator(bottom_zero)
    except Exception as e:
        assert isinstance(e, InvalidClassParameter), 'InvalidClassParameter'
    try:
        tuple_seq = TupleSequenceGenerator(bottom_zero)
    except Exception as e:
        assert isinstance(e, InvalidClassParameter), 'InvalidClassParameter'
    try:
        dict_seq = DictSequenceGenerator(bottom_zero)
    except Exception as e:
        assert isinstance(e, InvalidClassParameter), 'InvalidClassParameter'
    try:
        set_seq = SetSequenceGenerator(bottom_zero)
    except Exception as e:
        assert isinstance(e, InvalidClassParameter), 'InvalidClassParameter'
    list_seq = (
        ListSequenceGenerator(1),
        ListSequenceGenerator(10),
        ListSequenceGenerator()
    )
    tuple_seq = (
        TupleSequenceGenerator(1),
        TupleSequenceGenerator(10),
        TupleSequenceGenerator()
    )
    dict_seq = (
        DictSequenceGenerator(1),
        DictSequenceGenerator(10),
        DictSequenceGenerator()
    )
    set_seq = (
        SetSequenceGenerator(1),
        SetSequenceGenerator(10),
        SetSequenceGenerator()
    )
    rand_start = random.randint(-20, 0)
    rand_end = random.randint(20, 50)
    rand_step = random.randint(1, 2)
    rand_tuple = (random.randint(-10, 10), random.randint(-8, 8))
    file_type = random.choice(['json', 'xml'])
    try:
        list_seq[0].generate_fibonacci_sequence(file_type, rand_tuple, rand_end)
    except Exception as e:
        assert isinstance(e, InvalidSequenceLen), 'InvalidSequenceLen'
    try:
        tuple_seq[0].generate_range_sequence(file_type, rand_start, rand_end)
    except Exception as e:
        assert isinstance(e, InvalidSequenceLen), 'InvalidSequenceLen'
    try:
        set_seq[0].generate_fibonacci_sequence(file_type, rand_tuple, rand_end)
    except Exception as e:
        assert isinstance(e, InvalidSequenceLen), 'InvalidSequenceLen'
    try:
        dict_seq[0].generate_range_sequence(file_type, rand_start, rand_end)
    except Exception as e:
        assert isinstance(e, InvalidSequenceLen), 'InvalidSequenceLen'
    set_seq[2].generate_range_sequence(file_type, rand_start, 31)
    try:
        tuple_seq[1].get_sequence()
    except Exception as e:
        assert isinstance(e, InvalidSequenceLen), 'InvalidSequenceLen'
    try:
        set_seq[1].get_sequence()
    except Exception as e:
        assert isinstance(e, InvalidSequenceLen), 'InvalidSequenceLen'
    try:
        list_seq[1].get_sequence()
    except Exception as e:
        assert isinstance(e, InvalidSequenceLen), 'InvalidSequenceLen'
    try:
        dict_seq[1].get_sequence()
    except Exception as e:
        assert isinstance(e, BadSeqType), 'BadSeqType'
    dict_seq[2].generate_range_sequence(file_type, rand_start, 31)
    try:
        set_seq[1].get_sequence()
    except Exception as e:
        assert isinstance(e, BadSeqType), 'BadSeqType'
    try:
        list_seq[1].get_sequence()
    except Exception as e:
        assert isinstance(e, BadSeqType), 'BadSeqType'
    try:
        tuple_seq[1].get_sequence()
    except Exception as e:
        assert isinstance(e, BadSeqType), 'BadSeqType'
    tuple_seq[2].generate_range_sequence('json', rand_start, 31)
    os.remove(PATH_JSON)
    assert list_seq[1].get_sequence() == [], 'No file error'
    assert tuple_seq[1].get_sequence() == (), 'No file error'
    assert set_seq[1].get_sequence() == set(), 'No file error'
    assert dict_seq[1].get_sequence() == {}, 'No file error'

    set_seq[2].generate_range_sequence('json', rand_start, rand_end, rand_step)
    with open(PATH_JSON, 'r+') as file:
        file.seek(random.randint(3, 6))
        json.dump('<I live Python>', file)
    try:
        list_seq[2].get_sequence()
    except Exception as e:
        assert isinstance(e, InvalidJson), 'InvalidJson'
    tuple_seq[2].generate_range_sequence(
        'json', rand_start, rand_end, rand_step
    )
    assert tuple_seq[2].get_sequence() == tuple(
        [i for i in range(rand_start, rand_end, rand_step)]
    ), 'overwrite error'

    dict_seq[2].generate_fibonacci_sequence('xml', rand_tuple, 4)
    with open(PATH_XML, 'r+') as file:
        file.seek(random.randint(3, 6))
        json.dump('<I live Python>', file)
    try:
        dict_seq[2].get_sequence()
    except Exception as e:
        assert isinstance(e, InvalidXML), 'InvalidXML'
    dict_seq[2].generate_range_sequence(
        'xml', rand_start, rand_end, rand_step
    )
    try:
        dict_seq[2].get_sequence()
    except Exception as e:
        assert isinstance(e, InappropriateTypeForFiboGeneration), (
            'get fibo dict'
        )
    test_type_data = [
        random.sample(range(1, 7), 6),
        tuple(random.sample(range(-7, 7), 6)),
        set(random.sample(range(10, 17), 3)),
        str(random.randint(-10000000000, 10000000)),
        random.uniform(-1000000000.0, 100000000000.0),
        {1: 11, 2: 22, 3: 33},
        lambda x: x + 2,
        '', [], {}, (), True, False, None,
    ]
    for i in test_type_data:
        try:
            set_seq[2].generate_fibonacci_sequence(i, rand_tuple, 10)
        except Exception as e:
            assert isinstance(e, InvalidFileTypeArgument), 'Invalid first arg'
        try:
            tuple_seq[2].generate_fibonacci_sequence(file_type, (0, i), 10)
        except Exception as e:
            assert isinstance(e, IncorrectArgumentTypeError), 'Invalid sec arg'
        try:
            list_seq[2].generate_fibonacci_sequence(file_type, (i, 0), 10)
        except Exception as e:
            assert isinstance(e, IncorrectArgumentTypeError), 'Invalid sec arg'
        try:
            tuple_seq[2].generate_fibonacci_sequence(file_type, rand_tuple, i)
        except Exception as e:
            assert isinstance(e, IncorrectArgumentTypeError), 'Invalid last arg'
        try:
            list_seq = TupleSequenceGenerator(i)
        except Exception as e:
            assert isinstance(e, InvalidClassParameter), 'len arg'
        try:
            set_seq[2].generate_fibonacci_sequence(
                file_type, (rand_start, rand_start), 10
            )
        except Exception as e:
            assert isinstance(e, InappropriateTypeForFiboGeneration), (
                'first_fib = sec_fib'
            )
        try:
            dict_seq[2].generate_fibonacci_sequence(
                file_type, (rand_start, rand_start), 10
            )
        except Exception as e:
            assert isinstance(e, InappropriateTypeForFiboGeneration), (
                'first_fib = sec_fib'
            )
            

if __name__ == '__main__':
    test_positive()
    test_negative()
