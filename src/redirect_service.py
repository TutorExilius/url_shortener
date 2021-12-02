from typing import Optional

import flask

import app_globals
from db_manager import DBManager
from models import RedirectUrl


class RedirectService:
    def __init__(self, request: flask.Request):
        self.request = request
        self.db_manager = DBManager(url=app_globals.DATABASE_URL)

    def parse(self, identifier: str) -> Optional[str]:
        return self.db_manager.get_redirect_url(identifier=identifier)

    def add(self, identifier: str, redirect_url: str) -> None:
        self.db_manager.add_redirect(identifier, redirect_url)

    def create_and_add(self, redirect_uri: str) -> str:
        return self.db_manager.create_redirect(redirect_uri)

    def get_redirect_url(self, identifier: str) -> Optional[RedirectUrl]:
        return self.db_manager.get_redirect_url(identifier=identifier)

    def count_redirect(self, identifier: str) -> Optional[int]:
        return self.db_manager.count_redirect(identifier)
