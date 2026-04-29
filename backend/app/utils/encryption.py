import os
from cryptography.fernet import Fernet
from flask import current_app

def get_cipher():
    # In production, this key must be securely managed (e.g. AWS KMS)
    key_str = os.environ.get("E2E_ENCRYPTION_KEY")
    if not key_str:
        # Generate a dummy key for local dev if not provided
        # In a real scenario, failing here is safer
        key_str = Fernet.generate_key().decode()
        os.environ["E2E_ENCRYPTION_KEY"] = key_str
    
    return Fernet(key_str.encode())

def encrypt_message(plain_text: str) -> str:
    if not plain_text:
        return plain_text
    cipher = get_cipher()
    return cipher.encrypt(plain_text.encode()).decode()

def decrypt_message(encrypted_text: str) -> str:
    if not encrypted_text:
        return encrypted_text
    try:
        cipher = get_cipher()
        return cipher.decrypt(encrypted_text.encode()).decode()
    except Exception as e:
        print(f"⚠️ Decryption failed: {e}")
        return "[Encrypted Content - Decryption Failed]"
