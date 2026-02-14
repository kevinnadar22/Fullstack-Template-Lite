from typing import Generic, Optional, TypeVar

from pydantic.generics import GenericModel

T = TypeVar("T")


class APIResponse(GenericModel, Generic[T]):
    success: bool = True
    data: T
    message: Optional[str] = None

    model_config = {"populate_by_name": True}


class PaginatedResponse(APIResponse[T], Generic[T]):
    total: int
    page: int
    limit: int

    model_config = {"populate_by_name": True}
