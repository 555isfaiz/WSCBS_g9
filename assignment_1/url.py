import secrets

def value_gen():
    return secrets.token_hex(16)
