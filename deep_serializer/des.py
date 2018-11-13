import base64
import datetime
import sys
import typing
import uuid
from decimal import Decimal

from dateutil.parser import parse

from deep_serializer.aux import errors

try:
    # noinspection PyProtectedMember
    from typing import _GenericAlias as Generic
except ImportError:
    from typing import GenericMeta as Generic

__S = typing.TypeVar('__S')
__T = typing.TypeVar('__T')


def _convert_list(a: list, cls: typing.Type[__T]) -> typing.List[__T]:
    res = []
    for el in a:
        res.append(_DecAux.dict2class(cls, el))
    return res


def _convert_dict(d: dict, key_cls: typing.Type[__S], cls: typing.Type[__T]) -> typing.Dict[typing.Hashable, __T]:
    res = {}
    for k, v in d.items():
        res[_DecAux.dict2class(key_cls, k)] = _DecAux.dict2class(cls, v)
    return res


def _convert_set(a: list, cls: typing.Type[__T]) -> typing.Set[__T]:
    return set(_convert_list(a, cls))


def __get_name(c: Generic):
    if sys.version_info[:2] < (3, 7):
        return c.__origin__.__name__
    else:
        # noinspection PyProtectedMember
        return c._name


def _cnv_generic_alias(c: Generic, el):
    args = getattr(c, '__args__')
    tl = len(args)
    name = __get_name(c)
    if isinstance(el, (list, tuple)) and tl == 1 and name == 'List':
        return _convert_list(el, args[0])
    elif isinstance(el, dict) and tl == 2 and name == 'Dict':
        return _convert_dict(el, args[0], args[1])
    elif isinstance(el, (list, set, tuple)) and tl == 1 and name == 'Set':
        return _convert_set(el, args[0])
    return el


class _DecAux(object):
    @staticmethod
    def dict2class(c, el):
        try:
            if el is None or c is None:
                return el
            if isinstance(c, Generic):
                return _cnv_generic_alias(c, el)
            if not isinstance(c, type):
                return el
            if isinstance(el, c):
                return el
            if c == datetime.datetime:
                return parse(el)
            if c == Decimal:
                return Decimal(str(el))
            if c == uuid.UUID:
                if isinstance(el, bytes):
                    kw = 'bytes'
                elif isinstance(el, int):
                    kw = 'int'
                elif isinstance(el, str):
                    kw = 'hex'
                else:
                    raise TypeError('Bad uuid type')
                return uuid.UUID(**{kw: el})
            if c == bytes and isinstance(el, str):
                return base64.b64decode(el)
            if not isinstance(el, dict):
                return c(el)
            else:
                return c(**el)
        except TypeError as e:
            msg = 'Could not init class %s with dict %s, exception: %s' % (c, el, e.args)
            raise errors.DeserializeError(msg) from e


def cast(f):
    def new(*args, **kwargs):
        ann_dict = f.__annotations__
        a = []
        d = {}
        i = 0
        for el in args:
            n = f.__code__.co_varnames[i]
            c = ann_dict.get(n, None)
            tmp = _DecAux.dict2class(c, el)
            a.append(tmp)
            i += 1
        for k, v in kwargs.items():
            c = ann_dict.get(k, None)
            v = _DecAux.dict2class(c, v)
            d[k] = v
        return f(*a, **d)

    return new
