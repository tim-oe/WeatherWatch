import logging
import pprint
from typing import Type, TypeVar, cast

T = TypeVar("T")


def logger(cls: Type[T]) -> Type[T]:
    """
    decorator to add logger and to_string to classes
    """

    def to_string(self) -> str:
        """
        convert class to string
        :return: string representation of the class
        """
        return pprint.pformat(self.__dict__)

    # More explicit type handling
    cls.logger = logging.getLogger(cls.__name__)  # type: ignore[attr-defined]
    cls.__str__ = to_string  # type: ignore[assignment]

    return cast(Type[T], cls)
