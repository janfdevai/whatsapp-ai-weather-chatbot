from typing import Any, Optional


def merge_user(left: Optional[dict[str, Any]], right: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Reducer to merge user state updates."""
    if left is None:
        return right or {}
    if right is None:
        return left
    return {**left, **right}
