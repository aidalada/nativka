from math import ceil
from typing import Any, Sequence


def paginate(items: Sequence[Any], total: int, page: int, limit: int) -> dict[str, Any]:
    return {
        "items": list(items),
        "page": page,
        "limit": limit,
        "total": total,
        "pages": ceil(total / limit) if limit else 1,
    }



