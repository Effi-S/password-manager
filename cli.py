from typing import Optional

import click

from password_manager.database import Database
from password_manager.password_manager import PasswordManager


@click.group()
def cli(): ...


def check_key_file(ctx, param, value):
    return value or PasswordManager.retrieve_key_from_file()


def _create_password(ctx=None, param=None, value=None):
    if value:
        return value
    return PasswordManager.generate_password()


def choose_name(db: Database = None):
    """prompts the user to choose 1 of the items in the DB"""
    db = db or Database()
    names = db.get_names()
    s = "\n  ".join(f"{i} - {name}" for i, name in enumerate(names))
    choice = click.prompt(
        f"Please choose:\n  {s}\n",
        type=click.Choice(list(map(str, range(len(names)))), case_sensitive=False),
    )
    name = names[int(choice)]
    click.echo(f"You selected: ({choice}) {name}")
    return name


@cli.command()
@click.option(
    "--key",
    prompt=False,
    hide_input=True,
    callback=check_key_file,
    help="Master password key",
)
@click.option(
    "--name",
    "--title",
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
    callback=_create_password,
    help="Password to create",
)
def add(
    key: bytes, name: str, username: Optional[str], password: str, db: Database = None
):
    """Add a new Password"""
    manager = PasswordManager(key)
    db = db or Database()

    encrypted_pw = manager.encrypt(password)

    db.add_password(name=name, username=username, encrypted_password=encrypted_pw)
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
    "--name",
    "--title",
    prompt=False,
    help="What to call the password",
)
def view(key, name: Optional[str], db: Database = None):
    """View existing passwords"""
    db = db or Database()
    name = name or choose_name(db=db)

    manager = PasswordManager(key)

    entry = db.get(name=name)
    decrypted_pw = manager.decrypt(entry.encrypted_password)
    click.echo(
        f"Name: {entry.name}\nUsername: {entry.username}\nPassword: {decrypted_pw}"
    )


@cli.command()
@click.option(
    "--name",
    "--title",
    required=False,
    help="The name to update\nIf you want to Update the name itself, "
    "first provide the name and then the updated name",
)
@click.option("--password", prompt=False)
@click.option("--username", prompt=False)
def update(name: tuple[str], password: str, username: str, db: Database = None):
    """Update an existing password"""
    db = db or Database()
    name = name or choose_name()

    # TODO: Allow Name Update
    # if n := len(name) > 2:
    #     raise click.ClickException("--name excepts 1 or 2 values.")

    db.update(
        name=name,
        encrypted_password=password,
        new_name=None,  # TODO
        username=username,
    )
    click.echo(f"Updated {name}!")


@cli.command()
@click.option(
    "--name",
    "--title",
    required=False,
    help="The name to delete",
)
def delete(name: Optional[str], db: Database = None):
    """Delete an Entry in it's entirety"""
    name = name or choose_name()

    db = db or Database()
    db.delete(name)
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
    "--name",
    "--title",
    required=False,
    help="The name to Rotate",
)
def rotate(key: bytes, name: Optional[str], db: Database = None):
    """Create a new encrypted password, replacing the old one"""
    name = name or choose_name()
    pm = PasswordManager(key=key)
    password = pm.encrypt(_create_password())

    db = db or Database()
    db.update(
        name=name,
        encrypted_password=password,
    )
    click.echo(f"{name}'s password rotated!")


if __name__ == "__main__":
    cli()
