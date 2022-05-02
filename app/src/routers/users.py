from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from typing import List
from datetime import datetime, timedelta
import re # helps us check roles

from ..models import UserModel, ShowUserModel, UpdateUserModel, UserResponseModel
from ..dependencies import (
    get_current_user,
    get_password_hash
)

from ..settings import db


router = APIRouter(
    tags=['Users'],
    prefix='/users'
)

# endpoints

#create a new user
@router.post('/register', response_description='Register new user', response_model=UserResponseModel)
async def create_new_user(user: UserModel):
    #if re.match('manager|assembler|producer', user.role):
    user_in_db = await db['users'].find_one({'email': user.email})
    if user_in_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'User with email {user.email} already exists')
    else:

        datetime_now = datetime.now()
        user.created_at = datetime_now.strftime('%m/%d/%y %H:%M:%S')
        user.password = get_password_hash(user.password)
        user = jsonable_encoder(user)
        new_user = await db['users'].insert_one(user)
        await db['users'].update_one({'_id': new_user.inserted_id}, 
                                    {'$rename': {'password': 'hashed_pass'}})
        created_user = await db['users'].find_one({'_id': new_user.inserted_id})
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)

    #raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT, detail='User role not acceptable')


# get all users
@router.get('/list', response_description='List all users', response_model=List[ShowUserModel], status_code=status.HTTP_200_OK)
async def list_all_users():
    users = await db['users'].find().to_list(100)
    for user in users:
        user['is_active'] = 'false'
        try:
            last_login = datetime.strptime(user["last_login"], "%m/%d/%y %H:%M:%S")
            delta = datetime.now() - last_login
            if delta <= timedelta(days=30):
                user['is_active'] = 'true'
        except ValueError:
            pass
    return users

# get currently logged in user
@router.get('/current', response_description='Current logged in user', response_model=ShowUserModel)
async def current_user(current_user: ShowUserModel = Depends(get_current_user)):
    return current_user


# update users
@router.put('/manage/{user_id}', response_description='Update a user', response_model=ShowUserModel)
async def update_user(user_id: str, user: UpdateUserModel, current_user: UserModel = Depends(get_current_user)):
    if current_user['role'] == 'manager':
        user = {k: v for k,v in user.dict().items() if v is not None}
        
        if len(user) >= 1:
            update_result = await db['users'].update_one({'_id': user_id}, {'$set': user})

            if update_result.modified_count == 1:
                if (updated_user := await db['users'].find_one({'_id': user_id})) is not None:
                    return updated_user
        if (existing_user := await db['users'].find_one({'_id': user_id})) is not None:
            return existing_user
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id: {user_id} not found')
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'You do not have sufficient rights to modify content')


# delete users
@router.delete('/delete/{user_id}', response_description='Delete a user')
async def delete_user(user_id: str, current_user: UserModel = Depends(get_current_user)):
    if current_user['role'] == 'manager':
        delete_result = await db['users'].delete_one({'_id': user_id})

        if delete_result.deleted_count == 1:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id: {user_id} not found')
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Only managers can delete users')
    

