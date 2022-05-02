from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from .settings import pwd_context, db, oauth2_scheme, SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from typing import Optional


# hash the plain password using the inbuild method hash
def get_password_hash(password):
    return pwd_context.hash(password)


# verify whether the user input for password converted to a hash is the hashed password we stored
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# get a user based on their email
async def get_user(email: str):
    if (user := await db['users'].find_one({"email": email})) is not None:
        return user

    
# authenticate a user by checking whether all credentials are correct
async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return False
    if not verify_password(password, user['hashed_pass']):
        return False

    return user

# create an access token to be used while calling protected routes
def create_access_token(data: dict, expires_delta: Optional[timedelta]=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({'exp': expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

# get the currently logged in user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('email')
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception
    user = await get_user(username)
    if user is None:
        raise credentials_exception
    return user