import os
from typing import Optional

import dotenv

from password_manager.models import Password, Session, get_test_session

dotenv.load_dotenv()


class Database:
    def __init__(self, test: bool = False):
        self.test_mode = test or os.environ.get("TEST_DATABASE")
        self.session = Session() if not self.test_mode else get_test_session()

    def add_password(
        self, *, name: str, username: Optional[str] = None, encrypted_password: str
    ):
        new_entry = Password(
            name=name,
            username=username,
            encrypted_password=encrypted_password,
        )
        self.session.add(new_entry)
        self.session.commit()

    def get(self, name: str) -> Password:
        return self.session.query(Password).filter(Password.name == name).first()

    def get_names(self) -> list[str]:
        return [x.name for x in self.session.query(Password).all()]

    def update(
        self,
        name: str,
        new_name: str = None,
        encrypted_password: str = None,
        username: str = None,
    ):
        if not any((new_name, encrypted_password, username)):
            raise ValueError("Nothing was provided to Update")

        item = self.session.query(Password).filter(Password.name == name).first()

        if encrypted_password:
            item.encrypted_password = encrypted_password
        if username:
            item.username = username
        if new_name:
            item.name = new_name
        self.session.commit()

    def delete(self, name: str):
        item = self.session.query(Password).filter(Password.name == name).first()
        if item:
            self.session.delete(item)
            self.session.commit()

    def get_all(self):
        return self.session.query(Password).all()
