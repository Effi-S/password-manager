import base64
import os
import secrets
import string
from pathlib import Path

import dotenv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

KEYFILE = Path(__file__).parent / ".key"


MIN_PASS_LENGTH, DEFAULT_PASS_LENGTH = 5, 12
KEYSIZE = 32
PUNCTUATION = "!#&*+-/:;<=>@[]^_`{|}~"
CHARS = string.ascii_letters + string.digits + PUNCTUATION


class PasswordManager:
    def __init__(self, key: bytes):
        if isinstance(key, str):
            key = base64.b64decode(key)
        if len(key) != KEYSIZE:
            raise ValueError(f"Key must be of length: {KEYSIZE}. not {len(key)}")
        self.key = key

    def encrypt(self, data: str) -> str:
        # --1-- IV
        iv = os.urandom(16)

        # --2-- Create Cipher and encryptor
        print("Key:", self.key)
        cipher = Cipher(
            algorithms.AES(self.key), modes.CBC(iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()

        #  --3-- Add Padding (multiple of 16)
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data.encode()) + padder.finalize()

        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # --4-- Combine IV and encrypted data
        encrypted_data = iv + encrypted_data

        # --5-- base64 encode
        return base64.b64encode(encrypted_data).decode()

    def decrypt(self, data: str) -> str:
        if missing_padding := len(data) % 4:
            data += "=" * (4 - missing_padding)
        # --1-- Base64 decode
        data = base64.b64decode(data.encode())

        # --2-- Extract IV
        iv, encrypted_data = data[:16], data[16:]

        # --3-- Create Cipher and decryptor
        cipher = Cipher(
            algorithms.AES(self.key), modes.CBC(iv), backend=default_backend()
        )

        decryptor = cipher.decryptor()

        # --4-- Decrypt
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

        # --5-- Remove Padding
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        return data.decode()

    @staticmethod
    def generate_key() -> bytes:
        return base64.b64encode(os.urandom(KEYSIZE))

    @staticmethod
    def generate_password(length: int = DEFAULT_PASS_LENGTH) -> str:
        length = max(length, MIN_PASS_LENGTH)
        password = "".join(
            (
                secrets.choice(string.ascii_lowercase),
                secrets.choice(string.ascii_uppercase),
                secrets.choice(string.digits),
                secrets.choice(PUNCTUATION),
            )
        )
        for _ in range(length - len(password)):
            password += secrets.choice(CHARS)

        return password

    @staticmethod
    def retrieve_key_from_file() -> bytes:
        # TODO: Argon2 for PBKDF / Password lock the file
        # FIXME: Make this Secure with Keystore
        # TODO: Handle key Rotation
        if not KEYFILE.exists():
            KEYFILE.touch()
        key = dotenv.get_key(KEYFILE, "key", encoding="utf-8")
        if not key:
            key = PasswordManager.generate_key().decode("utf-8")
            dotenv.set_key(KEYFILE, "key", key, quote_mode="never")
        return base64.b64decode(key)


if __name__ == "__main__":
    # Usage example:
    key = PasswordManager.generate_key()
    pm = PasswordManager(key)
    encrypted = pm.encrypt("my secret password")
    print(f"Encrypted: {encrypted}")
    decrypted = pm.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
