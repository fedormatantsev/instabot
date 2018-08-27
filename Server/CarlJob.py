from CarlPostInfo import CarlPostInfo

import typing

JobValidateFunction = typing.Callable[[object], bool]


class Job:
    _tag: str
    _count: int
    _validate: JobValidateFunction

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def count(self) -> int:
        return self._count

    def check_post(self, post_info: CarlPostInfo) -> bool:
        return self._validate(post_info)

    def __init__(self, tag: str, count: int, validate: JobValidateFunction):
        self._tag = tag
        self._count = count
        self._validate = validate
