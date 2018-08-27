import typing


class CarlPostInfo:
    _tags: typing.List[str]
    _url: str
    _author: str
    _likes: int

    def __init__(self, tags: typing.List[str], url: str, author: str, likes: int):
        self._tags = tags
        self._url = url
        self._author = author
        self._likes = likes

    @property
    def tags(self) -> typing.List[str]:
        return self._tags

    @property
    def url(self) -> str:
        return self._url

    @property
    def author(self) -> str:
        return self._author

    @property
    def likes(self) -> int:
        return self._likes
