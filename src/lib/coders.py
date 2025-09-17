from decimal import Decimal

import msgspec

encoder = msgspec.json.Encoder()

decoder = msgspec.json.Decoder()


json_encoder = encoder

json_decoder_decimal = msgspec.json.Decoder(float_hook=Decimal)
