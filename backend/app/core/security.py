import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncar de seguridad a 72 bytes por el límite nativo de bcrypt
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def get_password_hash(password: str) -> str:
    # Truncar de seguridad a 72 bytes y generar el hash con bcrypt directamente
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')