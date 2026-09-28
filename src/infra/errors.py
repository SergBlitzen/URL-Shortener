from sqlalchemy.exc import IntegrityError

from infra.orm import SHORT_LINK_CODE_UNIQUE_CONSTRAINT


POSTGRES_UNIQUE_VIOLATION = "23505"


def is_short_link_code_conflict(
    exc: IntegrityError,
) -> bool:
    if getattr(exc.orig, "sqlstate", None) != POSTGRES_UNIQUE_VIOLATION:
        return False

    original_exc = exc.orig.__cause__

    return (
        original_exc is not None
        and getattr(original_exc, "constraint_name", None)
        == SHORT_LINK_CODE_UNIQUE_CONSTRAINT
    )