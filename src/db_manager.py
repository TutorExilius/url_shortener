from datetime import datetime
from typing import Optional

import shortuuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import RedirectType, RedirectUrl, UriType


class DBManager:
    def __init__(self, url: str):
        """Initialize a db_manager instance.

        :param url: Complete url within engine, user, password, port etc.
        """
        self._url = url

        # bind and create session
        Session = sessionmaker()
        engine = create_engine(self._url, echo=True)  # debug only
        Session.configure(bind=engine)
        self.session = Session()

    def add_redirect(self, identifier: str, redirect_url: str) -> None:
        utc_now = datetime.utcnow()
        redirect_identifier = self._next_uuid(excepted_uuids=[identifier])

        self.url = RedirectUrl(
            identifier=identifier,
            redirect_uri=redirect_identifier,
            uri_type=UriType.IDENTIFIER,
            redirect_type=RedirectType.PERM,
            activate_at=utc_now,
            created_at=utc_now,
        )
        perm_redirect_url = self.url

        temp_redirect_url = RedirectUrl(
            identifier=redirect_identifier,
            redirect_uri=redirect_url,
            uri_type=UriType.URL,
            redirect_type=RedirectType.TEMP,
            activate_at=utc_now,
            created_at=utc_now,
        )

        self.session.add(perm_redirect_url)
        self.session.add(temp_redirect_url)
        self.session.commit()

    def _next_uuid(self, excepted_uuids=None) -> str:
        if excepted_uuids is None:
            excepted_uuids = []

        generated_identifier = shortuuid.ShortUUID().random(length=8)

        while (
            self.get_redirect_url(generated_identifier) is not None
            or generated_identifier in excepted_uuids
        ):
            generated_identifier = shortuuid.ShortUUID().random(length=8)

        return generated_identifier

    def create_redirect(self, redirect_url: str) -> str:
        generated_identifier = self._next_uuid()
        self.add_redirect(identifier=generated_identifier, redirect_url=redirect_url)
        return generated_identifier

    def get_redirect_url(self, identifier: str) -> Optional[RedirectUrl]:
        redirect_url = (
            self.session.query(RedirectUrl)
            .filter(
                RedirectUrl.identifier == identifier,
                RedirectUrl.is_active(),
            )
            .first()
        )

        return redirect_url

    def count_redirect(self, identifier: str) -> Optional[int]:
        redirect_url = (
            self.session.query(RedirectUrl)
            .filter(
                RedirectUrl.identifier == identifier,
                RedirectUrl.is_active(),
            )
            .first()
        )

        if redirect_url:
            redirect_url.redirect_counter += 1
            self.session.commit()
            return redirect_url.redirect_counter

        return None
