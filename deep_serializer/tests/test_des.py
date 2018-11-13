import unittest

import datetime
import typing

from deep_serializer.aux.example import Car
from deep_serializer.des import _DecAux

try:
    # noinspection PyProtectedMember
    from typing import _GenericAlias as Generic
except ImportError:
    from typing import GenericMeta as Generic


class TestStringMethods(unittest.TestCase):

    def __aux(self, c, el, res):
        cnv = _DecAux.dict2class(c, el)
        self.assertEqual(cnv, res, '%s: %s != %s' % (c, cnv, res))

    def test_conv(self):
        self.__aux(typing.Union[int, float, str], '7', '7')
        self.__aux(datetime.datetime, '2015-01-01T00:00:00', datetime.datetime(2015, 1, 1))

    def test_car(self):
        car_dict = {
            'color': 'blue',
            'model': 'Volvo',
            'owner': {'age': '22', 'name': 'Bob'},
            'passengers': [{'age': 20, 'name': 'Alice'}, {'age': 19, 'name': 'Joe'}],
            'registration_date': '2015-01-01 12:00.00',
            'miles': {'2015-01-01 12:00.00': 0, '2016-01-01 12:00.00': '1000'}
        }
        expected_result = {'color': 'blue',
                           'miles': {datetime.datetime(2015, 1, 1, 12, 0): 0.0,
                                     datetime.datetime(2016, 1, 1, 12, 0): 1000.0},
                           'model': 'Volvo',
                           'owner': {'age': 22, 'name': 'Bob'},
                           'passengers': [{'age': 20, 'name': 'Alice'}, {'age': 19, 'name': 'Joe'}],
                           'registration_date': datetime.datetime(2015, 1, 1, 12, 0)}

        car = Car(**car_dict)
        self.assertTrue(expected_result == car.todict())
        self.assertDictEqual(expected_result, car.todict())
        car.registration_date += datetime.timedelta(days=12)
        self.assertFalse(expected_result == car.todict())
