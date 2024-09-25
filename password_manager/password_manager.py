import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class PasswordManager:
    def __init__(self, key: bytes):
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes (256 bits) long.")
        self.key = key

    def encrypt(self, data: str) -> str:
        # --1-- IV
        iv = os.urandom(16)

        # --2-- Create Cipher and encryptor
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
        return os.urandom(32)


if __name__ == "__main__":
    # Usage example:
    key = PasswordManager.generate_key()
    pm = PasswordManager(key)
    encrypted = pm.encrypt("my secret password")
    print(f"Encrypted: {encrypted}")
    decrypted = pm.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
