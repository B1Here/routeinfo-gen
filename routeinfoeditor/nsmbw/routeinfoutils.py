import re


def is_level_point(name: str) -> bool:
    return re.match(r"^W[1-9](?:S[0-1]|K[0-3]|[ACGTWX]0|0[1-9])$", name) is not None


def is_flag_point(name: str) -> bool:
    return re.match(r"^F[0-9abcdkls][0-9C]{2}$", name) is not None


def is_key_point(name: str) -> bool:
    return re.match(r"^K[a0-9][0-9][0-9a-f]$", name) is not None


def is_point(name: str) -> bool:
    return is_level_point(name) or is_flag_point(name) or is_key_point(name)
