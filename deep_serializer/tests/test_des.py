import datetime
import typing
import unittest

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
