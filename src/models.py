from __future__ import annotations

import http
from datetime import datetime
from enum import auto, IntEnum

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm import declarative_base, DeclarativeMeta

Base: DeclarativeMeta = declarative_base()


class UriType(IntEnum):
    IDENTIFIER = auto()
    URL = auto()


class RedirectType(IntEnum):
    PERM = http.HTTPStatus.PERMANENT_REDIRECT
    TEMP = http.HTTPStatus.TEMPORARY_REDIRECT


class RedirectUrl(Base):
    __tablename__ = "redirect_urls"

    id = Column(Integer, primary_key=True)
    identifier = Column(String, unique=True)
    redirect_uri = Column(String)
    uri_type = Column(Enum(UriType))
    redirect_type = Column(Enum(RedirectType))
    redirect_counter = Column(Integer, default=0)
    activate_at = Column(DateTime)
    deactivate_at = Column(
        DateTime,
        nullable=True,
        default=None,
    )  # can be None. None = always active
    created_at = Column(DateTime)

    @hybrid_method
    def is_active(self) -> bool:
        ret = (self.activate_at <= datetime.utcnow()) & (
            self.deactivate_at.is_(None) | (datetime.utcnow() <= self.deactivate_at)
        )
        return ret
