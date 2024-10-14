from functools import partial
from pathlib import Path

import streamlit as st

from password_manager.database import Database
from password_manager.password_manager import PasswordManager


def copy_to_clipboard(text: str):
    import pyperclip

    pyperclip.copy(text)


if "generated_password" not in st.session_state:
    st.session_state.generated_password = PasswordManager.generate_password()


if "key" not in st.session_state:
    st.session_state.key = PasswordManager.retrieve_key_from_file()

if "db" not in st.session_state:
    st.session_state.db = Database()

db = st.session_state.db

if "password_entries" not in st.session_state:
    st.session_state.password_entries = db.get_all()


with st.sidebar:
    st.write("# Password Manager")
    master_password = st.text_input(
        "Master Password", value="***", type="password", key="master-password"
    )

st.title("**Password Manager**")
add_tab, view_tab = st.tabs(["Add", "View/Update"])
with add_tab:
    st.write("### Add a new Password")
    c1, c2 = st.columns([0.8, 0.3])
    with c1:
        name = st.text_input("Name", key="add_name")
        username = st.text_input("Username (optional)", key="add_username")
        password = st.text_input(
            "Password",
            value=st.session_state.generated_password,
            type="password",
            key="add_password",
        )
    with c2:
        if st.button(label="Rotate Password"):
            st.session_state.generated_password = PasswordManager.generate_password()

        if st.button(label="Add Password", key="submit_button"):
            if name in db.get_names():
                st.error(f"Name: {name} already in use!")
            else:
                encrypted_pw = PasswordManager(st.session_state.key).encrypt(password)
                db.add_password(
                    name=name, username=username, encrypted_password=encrypted_pw
                )
                st.success("Password saved!")
                st.session_state.password_entries = db.get_all()


with view_tab:

    if not st.session_state.password_entries:
        st.info("No passwords yet.")
    for i, entry in enumerate(st.session_state.password_entries):
        with st.expander(f"Name: {entry.name}", expanded=False):
            st.session_state[f"c1_{i}"], st.session_state[f"c2_{i}"] = st.columns(
                [0.8, 0.3]
            )
            with st.session_state[f"c1_{i}"]:
                username_input = st.text_input(
                    label="Username:",
                    value=entry.username or "",
                    key=f"username_input_{i}",
                )
                if f"display_password_value_{i}" not in st.session_state:
                    decrypted_pw = PasswordManager(st.session_state.key).decrypt(
                        entry.encrypted_password
                    )
                    st.session_state[f"display_password_value_{i}"] = decrypted_pw
                password_input = st.text_input(
                    label="Password:",
                    value=st.session_state[f"display_password_value_{i}"],
                    type="password",
                    key=f"display_password_{i}",
                )
            with st.session_state[f"c2_{i}"]:
                st.button(
                    label="Copy",
                    on_click=partial(
                        copy_to_clipboard,
                        st.session_state[f"display_password_value_{i}"],
                    ),
                    key=f"copy_{entry.name}",
                )

                if st.button("Rotate Password", key=f"rotate_button_{i}"):
                    pm = PasswordManager(key=st.session_state.key)
                    new_password = PasswordManager.generate_password()
                    encrypted_pw = pm.encrypt(password)
                    st.session_state[f"display_password_value_{i}"] = new_password

                if st.button("Save Changes", key=f"update_button_{i}"):
                    with st.spinner("Processing..."):
                        encrypted_pw = PasswordManager(st.session_state.key).encrypt(
                            password_input
                        )

                        db.update(
                            name=entry.name,
                            encrypted_password=encrypted_pw,
                            username=username_input,
                        )

                        st.success(f"Updated {entry.name}!")
                        st.session_state.password_entries = db.get_all()

                if st.button("Delete Password", key=f"delete_button_{entry.name}"):
                    with st.spinner("Processing..."):
                        try:
                            db.delete(entry.name)
                        except Exception as e:
                            st.error(f"Error deleting {entry.name}: {str(e)}")
                        else:
                            st.success(f"Deleted {entry.name}!")
                            st.session_state.password_entries = db.get_all()
                            st.rerun()


def script_endpoint():
    import subprocess

    subprocess.run(["streamlit", "run", str(Path(__file__).resolve())])
