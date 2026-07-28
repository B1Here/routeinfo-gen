from collections.abc import Iterable
from typing import TypeGuard, TypeVar

T = TypeVar("T")


def is_defined(obj: T | None) -> TypeGuard[T]:
    return obj is not None


def split_if_contains(text: str, sep: str) -> Iterable[str]:
    return (
        [text]
        if not text.__contains__(sep)
        else filter(lambda f: f.strip(), text.split(sep))
    )
