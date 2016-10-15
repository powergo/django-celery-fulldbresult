from kombu.serialization import registry as k_registry
from kombu.exceptions import (EncodeError, DecodeError)


def dumps(data):
    """Serializes data using Kombu serializer, default format is JSON.
    """
    try:
        content_type, encoding, data = k_registry.dumps(data)
    except EncodeError as e:
        raise TypeError(e)
    return data


def loads(data, content_type="application/json", encoding="utf-8"):
    """Deserializes data using Kombu deserializer, default format is JSON.
    """
    try:
        return k_registry.loads(data, content_type, encoding)
    except DecodeError as e:
        raise TypeError(e)
