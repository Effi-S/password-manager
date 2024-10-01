from functools import partial

import pyperclip
import streamlit as st

from password_manager.database import Database
from password_manager.password_manager import PasswordManager


def _create_password():
    return PasswordManager.generate_password()


def copy_to_clipboard(text: str):
    pyperclip.copy(text)


def choose_name(db: Database):
    """Prompts the user to choose 1 of the items in the DB"""
    names = db.get_names()
    name = st.selectbox("Please choose Name:", options=names)
    if name:
        st.write(f"You selected: {name}")
        return name
    return None


# Streamlit App
st.sidebar.write("# Password Manager", anchor="top")

choice = st.sidebar.radio(
    "Choose an action",
    options=["Add", "View", "Update", "Delete", "Rotate"],
    horizontal=True,
)
master_password = st.sidebar.text_input(
    "Master Password", value="***", type="password", key="master-password"
)

key = PasswordManager.retrieve_key_from_file()

db = Database()

if choice == "Add":
    st.subheader("Add a new Password")
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
    st.subheader("View existing passwords")
    name = choose_name(db)

    if st.button("View Password") and name:
        manager = PasswordManager(key)
        entry = db.get(name=name)
        if entry:
            decrypted_pw = manager.decrypt(entry.encrypted_password)
            st.write(f"Name: {entry.name}")
            if entry.username:
                st.write(f"Username: {entry.username}")
            st.text_input(label="Password:", value=decrypted_pw, type="password")
            st.button(label="Copy", on_click=partial(copy_to_clipboard, decrypted_pw))

elif choice == "Update":
    st.subheader("Update an existing password")
    name = choose_name(db)
    password = st.text_input(
        "New password (optional)", type="password", key="update_password"
    )
    username = st.text_input("New username (optional)", key="update_username")

    if st.button("Update Password"):
        db.update(name=name, encrypted_password=password, username=username)
        st.success(f"Updated {name}!")

elif choice == "Delete":
    st.subheader("Delete an Entry in its entirety")
    name = choose_name(db)
    if st.button("Delete Password"):
        db.delete(name)
        names = db.get_names()
        st.write("Remaining passwords:")
        for i, name in enumerate(names):
            st.write(f"({i}) - {name}")

elif choice == "Rotate":
    st.subheader("Rotate a password")
    name = choose_name(db)
    if st.button("Rotate Password"):
        pm = PasswordManager(key=key)
        password = pm.encrypt(_create_password())
        db.update(name=name, encrypted_password=password)
        st.success(f"{name}'s password rotated!")

st.sidebar.divider()
