from typing import Any

from typeguard import TypeCheckError, check_type


def check_type_bool(obj: Any, my_type, **kwargs) -> bool:
    try:
        check_type(obj, my_type, **kwargs)
        return True
    except TypeCheckError:
        return False
