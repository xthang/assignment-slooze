from typing import Optional, TypeVar, cast


T = TypeVar('T')


# non-null assertion operator (equivalent to ! in other language)
def nn(obj: Optional[T]) -> T:
    # assert obj is not None
    return cast(T, obj)
