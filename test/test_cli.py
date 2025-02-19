import pytest
from click.testing import CliRunner

from cli import cli
from password_manager.database import Database
from password_manager.password_manager import PasswordManager


@pytest.fixture
def temp_db():
    return Database(test=True)


@pytest.fixture
def runner():
    return CliRunner(env={"TEST_DATABASE": "true"})


test_key = PasswordManager.generate_key().decode("utf-8")
test_encrypted_password = PasswordManager(test_key).encrypt("mypassword")

# def test_add(runner, temp_db):
#     cmd_ = ["add", "--key", test_key, "--name", "testname", "--password", "mypassword"]
#     result = runner.invoke(cli, cmd_)
#     assert result.exit_code == 0, f"python cli.py {' '.join(cmd_)}"

#     entry = temp_db.get("testname")
#     assert entry is not None
#     assert "Password saved!" in result.output

#     cmd_ = ["add", "--key", test_key, "--name", "testname2"]
#     result = runner.invoke(cli, cmd_)
#     assert result.exit_code == 0, f"python cli.py {' '.join(cmd_)}"

#     entry = temp_db.get("testname2")
#     assert entry is not None
#     assert "Password saved!" in result.output


def test_view(runner, temp_db):

    # --1-- add an entry
    temp_db.delete("testname3")
    temp_db.add_password(
        name="testname3",
        username="testuser",
        encrypted_password=test_encrypted_password,
    )

    # --2-- view added entry
    cmd_ = ["view", "--key", test_key, "--name", "testname3"]
    result = runner.invoke(cli, cmd_)

    assert result.exit_code == 0
    assert "Name: testname3" in result.output
    assert "Username: testuser" in result.output
    assert "Password: mypassword" in result.output


def test_update(runner, temp_db):
    # --1-- Add an entry
    temp_db.add_password(
        name="testname4", username="olduser", encrypted_password=test_encrypted_password
    )

    # --2-- Update the entry
    result = runner.invoke(
        cli,
        [
            "update",
            "--name",
            "testname4",
            "--password",
            "newpassword",
            "--username",
            "newuser",
        ],
    )

    assert result.exit_code == 0
    entry = temp_db.get("testname4")
    assert entry.encrypted_password == "newpassword"
    assert entry.username == "newuser"
    assert "Updated testname4!" in result.output


def test_delete(runner, temp_db):
    # --1-- Add an entry
    temp_db.add_password(
        name="testname5",
        username="testuser",
        encrypted_password=test_encrypted_password,
    )

    # --2-- Delete it
    result = runner.invoke(cli, ["delete", "--name", "testname5"])

    assert result.exit_code == 0
    assert temp_db.get("testname5") is None
    assert "Left:" in result.output


def test_rotate(runner, temp_db):
    # --1-- Add an entry
    temp_db.add_password(
        name="testname6",
        username="testuser",
        encrypted_password=test_encrypted_password,
    )

    # --2-- Rotate the password
    result = runner.invoke(cli, ["rotate", "--key", test_key, "--name", "testname6"])

    assert result.exit_code == 0
    entry = temp_db.get("testname6")
    assert entry.encrypted_password != "mypassword"  # Ensure the password was rotated
    assert "testname6's password rotated!" in result.output


def test_copy(runner, temp_db):
    # --1-- Add an entry
    temp_db.delete("testname6")
    temp_db.add_password(
        name="testname6",
        username="testuser",
        encrypted_password=test_encrypted_password,
    )

    # --2-- Copy the password
    result = runner.invoke(cli, ["copy", "--key", test_key, "--name", "testname6"])

    assert result.exit_code == 0
    assert "`testname6` password copied to clipboard!" in result.output
    # TODO: Add clipboard verification here
