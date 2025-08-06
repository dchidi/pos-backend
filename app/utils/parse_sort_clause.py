from typing import List, Tuple
from app.constants.sort_order_enum import SortOrder


def parse_sort(clause: str | None) -> List[Tuple[str, SortOrder]]:
    sort_params: List[Tuple[str, SortOrder]] = []
    if clause:
        for part in clause.split(","):
            part = part.strip()
            if not part:
                continue
            if part.startswith("-"):
                field, direction = part[1:], SortOrder.DESC
            else:
                field, direction = part.lstrip("+"), SortOrder.ASC
            if field:
                sort_params.append((field, direction))
    return sort_params
