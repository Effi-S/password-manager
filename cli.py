import secrets
import string
from pathlib import Path
from typing import Optional

import click

from password_manager.database import Database
from password_manager.password_manager import PasswordManager

KEYFILE = Path(__file__).parent / ".key"
PASS_LENGTH = 12
PUNCTUATION = "!#&*+-/:;<=>@[]^_`{|}~"
CHARS = string.ascii_letters + string.digits + PUNCTUATION


@click.group()
def cli():
    pass


def check_key_file(ctx, param, value):
    # FIXME: Make this Secure with Keystore
    # TODO: Handle key Rotation
    if not KEYFILE.exists():
        KEYFILE.touch()
    key = KEYFILE.read_bytes().strip()
    if not key:
        key = PasswordManager.generate_key()
        KEYFILE.write_bytes(key)
    return key


def create_password(ctx=None, param=None, value=None):
    if value:
        return value
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(PUNCTUATION),
    ]
    password += [secrets.choice(CHARS) for _ in range(PASS_LENGTH - 4)]

    return "".join(password)


def choose_description(db: Database = None):
    """prompts the user to choose 1 of the items in the DB"""
    db = db or Database()
    names = db.get_names()
    s = "\n  ".join(f"{i} - {name}" for i, name in enumerate(names))
    choice = click.prompt(
        f"Please choose:\n  {s}\n",
        type=click.Choice(list(map(str, range(len(names)))), case_sensitive=False),
    )
    description = names[int(choice)]
    click.echo(f"You selected: ({choice}) {description}")
    return description


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
    help="What to call the password",
)
@click.option(
    "--password",
    prompt=False,
    hide_input=True,
    callback=create_password,
    help="Password to create",
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
        description = choose_description(db=db)

    entry = db.get(description=description)
    decrypted_pw = manager.decrypt(entry.encrypted_password)
    click.echo(
        f"Desc: {entry.description}\nUsername: {entry.username}\nPassword: {decrypted_pw}"
    )


@cli.command()
@click.option(
    "--description",
    required=False,
    help="The name to update\nIf you want to Update the name itself, "
    "first provide the name and then the updated name",
)
@click.option("--password", prompt=False)
@click.option("--username", prompt=False)
def update(description: tuple[str], password: str, username: str):
    """Update an existing password"""
    if not description:
        description = choose_description()
    # TODO: Allow description Update
    # if n := len(description) > 2:
    #     raise click.ClickException("--description excepts 1 or 2 values.")

    db = Database()
    db.update(
        description=description,
        encrypted_password=password,
        new_desc=None,  # TODO
        username=username,
    )


@cli.command()
@click.option(
    "--description",
    required=False,
    help="The name to delete",
)
def delete(description: Optional[str]):
    description = description or choose_description()

    db = Database()
    db.delete(description)
    names = db.get_names()
    click.echo("Left:\n  ", nl=False)
    click.echo("\n  ".join(f"({i}) - {name}" for i, name in enumerate(names)))


@cli.command()
@click.option(
    "--key",
    prompt=False,
    hide_input=True,
    callback=check_key_file,
    help="Master password key",
)
@click.option(
    "description",
    "--description",
    required=False,
    help="The name to Rotate",
)
def rotate(key: bytes, description: Optional[str]):
    """Create a new encrypted password, replacing the old one"""
    description = description or choose_description()
    pm = PasswordManager(key=key)
    password = pm.encrypt(create_password())

    db = Database()
    db.update(
        description=description,
        encrypted_password=password,
    )


if __name__ == "__main__":
    cli()
