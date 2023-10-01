from aiodal.oqm.views import _default_paginator, PaginateableT
from dataclasses import dataclass
from typing import List

from typing import Any, Dict, Mapping

from sqlalchemy.engine.result import _KeyType

_T = Any
_DictT = Dict[str, Any]
_MappingT = Mapping[_KeyType, _T]


@dataclass
class NextPageInfo:
    total_count: int
    next_url: str | None


def _get_total_count(results: List[_DictT]) -> int:
    return results[0]["total_count"]  # type: ignore # key error means boo boo


def get(
    results: List[_DictT],
    request_url: str,
    offset: int,
    limit: int,
    url_start_index: str = "/v1",
) -> NextPageInfo:
    """Hacked from the innerds of aiodal.oqm. We get the same pagination calculation but its more
    loosely coupled with what we need for basat in terms of types.

    Our list views should create RowMappings using `list(result.mappings())` to pass here.

    Args:
        results (List[RowMapping]): _description_
        request_url (str): _description_
        offset (int): _description_
        limit (int): _description_
        url_start_index (str, optional): _description_. Defaults to "/v1".

    Returns:
        Page: _description_
    """
    current_len = len(results)
    if current_len == 0:
        return NextPageInfo(total_count=0, next_url=None)

    # NOTE if this throws a KeyError we made a boo in sql stmt and forgot sa_total_count!
    total_count = _get_total_count(results)

    next_url = _default_paginator(
        request_url, offset, limit, current_len, total_count, url_start_index
    )
    return NextPageInfo(total_count=total_count, next_url=next_url)
