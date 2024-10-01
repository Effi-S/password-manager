import uuid
from functools import partial

import streamlit as st

from password_manager.database import Database
from password_manager.password_manager import PasswordManager


def _create_password():
    return PasswordManager.generate_password()


def copy_to_clipboard(text: str):
    import pyperclip

    pyperclip.copy(text)


def choose_name(db: Database, key: str):
    """Prompts the user to choose 1 of the items in the DB"""
    names = db.get_names()
    name = st.selectbox("Name:", options=names, key=key)
    # if name:
    #     st.write(f"You selected: {name}")
    return name


# Streamlit App
st.sidebar.write("# Password Manager")

add_tab, view_tab, update_tab, delete_tab, rotate_tab = st.tabs(
    ["Add", "View", "Update", "Delete", "Rotate"]
)

master_password = st.sidebar.text_input(
    "Master Password", value="***", type="password", key="master-password"
)

key = PasswordManager.retrieve_key_from_file()

db = Database()

with add_tab:
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

with view_tab:
    st.subheader("View existing passwords")
    name = choose_name(db, key="view_tab_key")
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

with update_tab:
    st.subheader("Update an existing password")
    name = choose_name(db, key="update_tab_key")
    password = st.text_input(
        "New password (optional)", type="password", key="update_password"
    )
    username = st.text_input("New username (optional)", key="update_username")

    if st.button("Update Password"):
        if not any((password, username)):
            st.time_input
            st.warning("Nothing was selected to change")
        else:
            st.success(f"Updated {name}!")
            password = PasswordManager(key).encrypt(password)
            db.update(name=name, encrypted_password=password, username=username)

with delete_tab:
    st.subheader("Delete an Entry in its entirety")
    name = choose_name(db, key="delete_tab_key")
    if st.button("Delete Password"):
        db.delete(name)
        names = db.get_names()
        st.write("Remaining passwords:")
        for i, name in enumerate(names):
            st.write(f"{i}) {name}")

with rotate_tab:
    st.subheader("Rotate a password")
    name = choose_name(db, key="rotate_tab_key")
    if st.button("Rotate Password"):
        pm = PasswordManager(key=key)
        password = pm.encrypt(_create_password())
        db.update(name=name, encrypted_password=password)
        st.success(f"{name}'s password rotated!")

st.sidebar.divider()
