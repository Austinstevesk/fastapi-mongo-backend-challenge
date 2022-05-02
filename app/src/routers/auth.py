from fastapi import APIRouter, status, HTTPException, Depends
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm

from ..settings import db, ACCESS_TOKEN_EXPIRE_MINUTES

from ..dependencies import (
    authenticate_user,
    create_access_token
)

router = APIRouter(
    tags=['Authentication'],
    prefix='/auth'
)
# get access token by login in, the details should be correct
@router.post('/login', status_code=status.HTTP_200_OK)
async def login_to_get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect ID or password",
                            headers={'WWW-Authenticate': 'Bearer'})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'email': user['email']}, expires_delta=access_token_expires
    )
    await db['users'].update_one({'email': form_data.username}, {'$set': {
        'last_login': datetime.now().strftime("%m/%d/%y %H:%M:%S"),
        'is_active': 'true' 
    }})
    return {'access_token': access_token, 'token_type': 'bearer'}
