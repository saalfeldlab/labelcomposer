from typing import Any, Union

from typeguard import TypeCheckError, check_type, typechecked

StringLike = Union[str, bytes, bytearray]


def check_type_bool(obj: Any, my_type, **kwargs) -> bool:
    try:
        check_type(obj, my_type, **kwargs)
        return True
    except TypeCheckError:
        return False


@typechecked
def convert_to_str(value: StringLike) -> str:
    if isinstance(value, (bytes, bytearray)):
        return value.decode()
    else:
        return value
