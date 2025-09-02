from datetime import date
from decimal import Decimal
from typing import Any

import msgspec

encoder = msgspec.json.Encoder()

decoder = msgspec.json.Decoder()


def json_encode_default(obj: Any) -> str:  # noqa: ANN401
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    error_message = f"Object {type(obj)} is not serializable"
    raise TypeError(error_message)


json_encoder = encoder

json_decoder_decimal = msgspec.json.Decoder(float_hook=Decimal)
