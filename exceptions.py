import typing

from fastapi.exceptions import HTTPException


class DependencyException(HTTPException):
    def __init__(self, status_code: int, detail_info: typing.Dict[str, typing.Any]):
        self.status_code = status_code
        self.detail_info = detail_info




