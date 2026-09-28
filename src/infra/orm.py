import datetime
import uuid

from sqlalchemy import DateTime, func, UniqueConstraint, String, text
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column


SHORT_LINK_CODE_UNIQUE_CONSTRAINT = "uq_short_links_code"


class Base(DeclarativeBase):
    pass


class ShortLinkORM(Base):
    __tablename__ = "short_links"
    __table_args__ = (
        UniqueConstraint(
            "code",
            name=SHORT_LINK_CODE_UNIQUE_CONSTRAINT,
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    external_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
    )
    url: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(
        String(6),
    )
    clicks_count: Mapped[int] = mapped_column(
        default=0,
        server_default=text("0"),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )
