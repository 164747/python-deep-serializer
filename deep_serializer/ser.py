import inspect
import json
from decimal import Decimal
from enum import Enum

import typing
import uuid

from deep_serializer.aux.errors import SerializeError
from deep_serializer.aux.formats.json import JsonEncoder


def __strip_val(v, strip):
    return isinstance(v, dict) and len(v) == 0 and strip


def __standard_type(obj):
    return obj is None or isinstance(obj, (str, int, float, bytes, bytearray, memoryview, Enum, Decimal, uuid.UUID))


def __ret_val(val: typing.Any, converter: typing.Callable[[typing.Any], typing.Any] = None) -> typing.Any:
    if converter is None:
        return val
    return converter(val)


def _todict(obj, strip=True, class_key=None, done_id=None, redo_objects=False, level=-1,
            key_converter: typing.Callable[[typing.Any], typing.Any] = None,
            value_converter: typing.Callable[[typing.Any], typing.Any] = None):
    further = (level != 0)
    further = further and not __standard_type(obj)

    if not redo_objects:
        if done_id is None:
            done_id = set([])
        obj_id = id(obj)
        further = further and obj_id not in done_id
        done_id.add(obj_id)

    if further:
        if isinstance(obj, dict):
            data = {}
            for k in obj.keys():
                val = _todict(obj[k], strip, class_key, done_id, redo_objects, level - 1, key_converter,
                              value_converter)
                if not __strip_val(val, strip):
                    data[__ret_val(k, key_converter)] = val
            return data
        elif isinstance(obj, set):
            return {_todict(v, strip, class_key, done_id, redo_objects, level - 1, key_converter, value_converter) for v
                    in obj}
        elif hasattr(obj, "__iter__"):
            return [_todict(v, strip, class_key, done_id, redo_objects, level - 1, key_converter, value_converter) for v
                    in obj]
        elif hasattr(obj, "__dict__") and getattr(obj, "__dict__") != {}:
            data = {}
            for key, preValue in obj.__dict__.items():
                if not callable(preValue) and not key.startswith('_') and not inspect.ismodule(preValue):
                    post_val = _todict(preValue, strip, class_key, done_id, redo_objects, level - 1, key_converter,
                                       value_converter)
                    if not __strip_val(post_val, strip):
                        data[__ret_val(key, key_converter)] = post_val
            if class_key is not None and hasattr(obj, "__class__"):
                data[class_key] = obj.__class__.__name__
            return data
    return __ret_val(obj, value_converter)


class ToDictEnabled(object):
    __T = typing.TypeVar('__T')

    def todict(self, strip=True, class_key=None, done_id=None, redo_objects=False, level=-1,
               key_converter: typing.Callable[[typing.Any], typing.Any] = None,
               value_converter: typing.Callable[[typing.Any], typing.Any] = None):
        try:
            return _todict(self, strip, class_key, done_id, redo_objects, level=level, key_converter=key_converter,
                           value_converter=value_converter)
        except BaseException as exc:
            raise SerializeError from exc

    @property
    def canonical_str(self) -> str:
        return self.canonical_json

    @property
    def canonical_json(self) -> str:
        try:
            return json.dumps(self.todict(), cls=JsonEncoder, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        except BaseException as exc:
            raise SerializeError from exc

    @property
    def canonical_bytes(self) -> bytes:
        return self.canonical_json.encode()

    @staticmethod
    def canonical_bytes2dict(cb: bytes) -> dict:
        s = cb.decode()
        return json.loads(s)

    @staticmethod
    def obj2dict(obj: object) -> dict:
        return _todict(obj)

    @staticmethod
    def get_canonical(data: dict, fmt: str) -> str:
        if fmt == 'json':
            return json.dumps(data, cls=JsonEncoder, sort_keys=True, separators=(',', ':'))
        raise NotImplementedError

    def __eq__(self, other):
        if isinstance(other, ToDictEnabled) and self.__class__ == other.__class__:
            return self.todict() == other.todict()
        return NotImplemented
