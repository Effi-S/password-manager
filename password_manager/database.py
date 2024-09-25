from typing import Optional

from password_manager.models import Password, Session


class Database:
    def __init__(self):
        self.session = Session()

    def add_password(
        self,
        *,
        description: str,
        username: Optional[str] = None,
        encrypted_password: str
    ):
        new_entry = Password(
            description=description,
            username=username,
            encrypted_password=encrypted_password,
        )
        self.session.add(new_entry)
        self.session.commit()

    def get(self, description: str) -> Password:
        return (
            self.session.query(Password)
            .filter(Password.description == description)
            .first()
        )

    def get_names(self) -> list[str]:
        return [x.description for x in self.session.query(Password).all()]

    def update(
        self,
        description: str,
        new_desc: str = None,
        password: str = None,
        username: str = None,
    ):
        if not any((new_desc, password, username)):
            raise ValueError("Nothing was provided to Update")

        item = (
            self.session.query(Password)
            .filter(Password.description == description)
            .first()
        )

        if password:
            item.encrypted_password = password
        if username:
            item.username = username
        if new_desc:
            item.description = new_desc
        self.session.commit()

    def delete(self, description: str):
        for item in (
            self.session.query(Password)
            .filter(Password.description == description)
            .all()
        ):
            self.session.delete(item)
        self.session.commit()
