import inspect
import json
import typing
import uuid
from decimal import Decimal
from enum import Enum

from deep_serializer.aux.errors import SerializeError
from deep_serializer.aux.formats.json import JsonEncoder


def __val_ok(v, strip):
    return strip is False or (not isinstance(v, dict) or len(v) > 0)


def __standard_type(obj):
    return obj is None or isinstance(obj, (str, int, float, bytes, bytearray, Enum, Decimal, uuid.UUID))


def _todict(obj, strip=True, class_key=None, done_id=None, redo_objects=False, level=-1):
    if level == 0:
        return obj

    if done_id is None:
        done_id = set([])

    if __standard_type(obj):
        return obj
    elif isinstance(obj, memoryview):
        return obj.tobytes()
    elif not redo_objects:
        obj_id = id(obj)
        if obj_id in done_id:
            return obj
        done_id.add(obj_id)

    if isinstance(obj, dict):
        for k in obj.keys():
            val = _todict(obj[k], strip, class_key, done_id, redo_objects, level - 1)
            if __val_ok(val, strip):
                obj[k] = val
        return obj
    elif isinstance(obj, set):
        return {_todict(v, strip, class_key, done_id, redo_objects, level - 1) for v in obj}
    elif hasattr(obj, "__iter__"):
        return [_todict(v, strip, class_key, done_id, redo_objects, level - 1) for v in obj]
    elif hasattr(obj, "__dict__") and getattr(obj, "__dict__") != {}:
        data = {}
        for key, preValue in obj.__dict__.items():
            if not callable(preValue) and not key.startswith('_') and not inspect.ismodule(preValue):
                post_val = _todict(preValue, strip, class_key, done_id, redo_objects, level - 1)
                if __val_ok(post_val, strip):
                    data[key] = post_val
        if class_key is not None and hasattr(obj, "__class__"):
            data[class_key] = obj.__class__.__name__
        return data
    else:
        return obj


class ToDictEnabled(object):
    __T = typing.TypeVar('__T')

    def todict(self, strip=True, class_key=None, done_id=None, redo_objects=False, level=-1):
        try:
            return _todict(self, strip, class_key, done_id, redo_objects, level=level)
        except BaseException as exc:
            raise SerializeError from exc

    @property
    def canonical_str(self) -> str:
        return self.canonical_json

    @property
    def canonical_json(self) -> str:
        try:
            return json.dumps(self.todict(), cls=JsonEncoder, sort_keys=True, separators=(',', ':'))
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
