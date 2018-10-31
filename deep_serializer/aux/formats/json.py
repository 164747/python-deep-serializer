import base64
import datetime
import enum
import json
import uuid
from decimal import Decimal


class JsonEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, uuid.UUID):
            return str(o)
        if isinstance(o, Decimal):
            return '{:f}'.format(o.normalize())
        if isinstance(o, enum.Enum):
            return o.value
        if isinstance(o, (bytes, bytearray)):
            return base64.b64encode(o).decode()
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return super().default(o)
