import getpass
import os
from pathlib import Path
from typing import Optional

import click

from password_manager.database import Database
from password_manager.password_manager import PasswordManager

KEYFILE = Path(__file__).parent / ".key"


@click.group()
def cli():
    pass


def check_key_file(ctx, param, value):
    # TODO: Make this Secure
    # TODO: Handle key Rotation
    if not KEYFILE.exists():
        KEYFILE.touch()
    key = KEYFILE.read_bytes().strip()
    if not key:
        key = PasswordManager.generate_key()
        KEYFILE.write_bytes(key)
    return key


@cli.command()
@click.option(
    "--key",
    prompt=False,
    hide_input=True,
    callback=check_key_file,
    help="Master password key",
)
@click.option(
    "--description",
    "--name",
    prompt=True,
    help="What to call the password",
)
@click.option(
    "--username",
    prompt=False,
    default=None,
    hide_input=True,
    help="What to call the password",
)
@click.option(
    "--password",
    prompt=True,
    confirmation_prompt=True,
    hide_input=True,
    help="Master password key",
)
def add(key: bytes, description: str, username: Optional[str], password: str):
    """Add a new Password"""
    manager = PasswordManager(key)
    print(key, username, password, description, sep="\n")
    db = Database()

    encrypted_pw = manager.encrypt(password)

    db.add_password(
        description=description, username=username, encrypted_password=encrypted_pw
    )
    click.echo("Password saved!")


@cli.command()
@click.option(
    "--key",
    prompt=False,
    hide_input=True,
    callback=check_key_file,
    help="Master password key",
)
@click.option(
    "--description",
    "--name",
    prompt=False,
    help="What to call the password",
)
def view(key, description: Optional[str]):
    """View existing passwords"""

    manager = PasswordManager(key)
    db = Database()

    if not description:
        names = db.get_names()
        s = "\n  ".join(f"{i} - {name}" for i, name in enumerate(names))
        choice = click.prompt(
            f"Please choose:\n  {s}\n",
            type=click.Choice(list(map(str, range(len(names)))), case_sensitive=False),
        )
        description = names[int(choice)]
        click.echo(f"You selected: ({choice}) {description}")

    entry = db.get(description=description)
    decrypted_pw = manager.decrypt(entry.encrypted_password)
    click.echo(
        f"Desc: {entry.description}\nUsername: {entry.username}\nPassword: {decrypted_pw}"
    )


if __name__ == "__main__":
    cli()
