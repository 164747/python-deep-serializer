import base64
import enum
import json
from decimal import Decimal

import datetime
import uuid


class JsonEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, uuid.UUID):
            return str(o)
        if isinstance(o, Decimal):
            return '{:f}'.format(o.normalize())
        if isinstance(o, enum.Enum):
            return o.value
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()

        if isinstance(o, memoryview):
            o = o.tobytes()
        if isinstance(o, (bytes, bytearray)):
            return base64.b64encode(o).decode()
        return super().default(o)
