from __future__ import annotations
from strawberry.types import Info
from typing import Callable, List, TypeVar, Optional

from .. import types


_T = TypeVar("_T")


def query_connection(
    info: Info,
    query_edges: Callable[..., List[types.Edge[_T]]],
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> types.Connection[_T]:

    # https://strawberry.rocks/docs/guides/pagination
    # https://relay.dev/graphql/connections.htm

    forward = after or (first is not None)
    backward = before or (last is not None)

    if forward and backward:
        raise ValueError("Only either after/first or before/last is allowed")

    if forward:
        if first is not None:
            first += 1  # add one for has_next_page
        edges = query_edges(info=info, after=after, first=first)
        has_previous_page = not not after
        if has_next_page := len(edges) == first:
            edges = edges[:-1]
    elif backward:
        if last is not None:
            last += 1  # add one for has_previous_page
        edges = query_edges(info=info, before=before, last=last)
        if has_previous_page := len(edges) == last:
            edges = edges[1:]
        has_next_page = not not before
    else:
        edges = query_edges(info)
        has_previous_page = False
        has_next_page = False

    page_info = types.PageInfo(
        has_previous_page=has_previous_page,
        has_next_page=has_next_page,
        start_cursor=edges[0].cursor if edges else None,
        end_cursor=edges[-1].cursor if edges else None,
    )

    return types.Connection(page_info=page_info, edges=edges)
