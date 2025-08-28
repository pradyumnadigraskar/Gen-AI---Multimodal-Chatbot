# from datetime import datetime, timedelta
# from jose import jwt
# from passlib.context import CryptContext
# from .config import settings

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

# def verify_password(password: str, pw_hash: str) -> bool:
#     return pwd_context.verify(password, pw_hash)

# def create_jwt(user_id: int) -> str:
#     expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
#     payload = {"sub": str(user_id), "exp": expire}
#     return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

# def decode_jwt(token: str) -> int | None:
#     try:
#         payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
#         return int(payload.get("sub"))
#     except Exception:
#         return None


from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_jwt(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def decode_jwt(token: str):
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
