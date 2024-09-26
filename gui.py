import streamlit as st

from password_manager.database import Database
from password_manager.password_manager import PasswordManager


def _create_password():
    return PasswordManager.generate_password()


def choose_name(db: Database):
    """Prompts the user to choose 1 of the items in the DB"""
    names = db.get_names()
    choice = st.selectbox(
        "Please choose:", options=[f"{i} - {name}" for i, name in enumerate(names)]
    )
    if choice:
        name = names[int(choice.split(" - ")[0])]
        st.write(f"You selected: {name}")
        return name
    return None


# Streamlit App
st.title("Password Manager")

choice = st.sidebar.selectbox(
    "Choose an action", ["Add", "View", "Update", "Delete", "Rotate"]
)

key = PasswordManager.retrieve_key_from_file()

db = Database()

if choice == "Add":
    st.header("Add a new Password")
    name = st.text_input("What to call the password", key="name")
    username = st.text_input("Username (optional)", key="username")
    password = st.text_input(
        "Password to create", value=_create_password(), type="password", key="password"
    )

    if st.button("Add Password"):
        manager = PasswordManager(key)
        encrypted_pw = manager.encrypt(password)
        db.add_password(name=name, username=username, encrypted_password=encrypted_pw)
        st.success("Password saved!")

elif choice == "View":
    st.header("View existing passwords")
    name = st.text_input(
        "What to call the password (leave blank to choose from list)", key="view_name"
    )
    if not name:
        name = choose_name(db)

    if st.button("View Password") and name:
        manager = PasswordManager(key)
        entry = db.get(name=name)
        if entry:
            decrypted_pw = manager.decrypt(entry.encrypted_password)
            st.write(f"Name: {entry.name}")
            st.write(f"Username: {entry.username}")
            st.write(f"Password: {decrypted_pw}")
        else:
            st.error("No such password found.")

elif choice == "Update":
    st.header("Update an existing password")
    name = st.text_input("The name to update", key="update_name")
    password = st.text_input(
        "New password (optional)", type="password", key="update_password"
    )
    username = st.text_input("New username (optional)", key="update_username")

    if st.button("Update Password"):
        if not name:
            name = choose_name(db)
        db.update(name=name, encrypted_password=password, username=username)
        st.success(f"Updated {name}!")

elif choice == "Delete":
    st.header("Delete an Entry in its entirety")
    name = st.text_input("The name to delete", key="delete_name")

    if st.button("Delete Password"):
        if not name:
            name = choose_name(db)
        db.delete(name)
        names = db.get_names()
        st.write("Remaining passwords:")
        for i, name in enumerate(names):
            st.write(f"({i}) - {name}")

elif choice == "Rotate":
    st.header("Rotate a password")
    name = st.text_input("The name to rotate", key="rotate_name")

    if st.button("Rotate Password"):
        if not name:
            name = choose_name(db)
        pm = PasswordManager(key=key)
        password = pm.encrypt(_create_password())
        db.update(name=name, encrypted_password=password)
        st.success(f"{name}'s password rotated!")
