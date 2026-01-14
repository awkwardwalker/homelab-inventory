from sqlalchemy import Boolean, Integer, Text, DateTime, func
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class HomeLabItem(Base):
    __tablename__ = "homelab_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)

    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)

    vlan_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vlan_name: Mapped[str | None] = mapped_column(Text, nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    public_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
