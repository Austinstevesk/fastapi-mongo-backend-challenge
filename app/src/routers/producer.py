from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from ..models import ComponentModel, ComponentShowModel, ComponentUpdateProducerModel
from ..settings import client
from typing import List

from ..models import ShowUserModel
from ..dependencies import get_current_user


db = client.components

router = APIRouter(
    tags=['producer'],
    prefix='/producer'
)


# add a component to the components document
@router.post('/add', response_description='Add a new component')
async def create_new_component(component: ComponentModel, current_user: ShowUserModel = Depends(get_current_user)):
    if current_user['role'] == 'producer' or current_user['role'] == 'manager':

        # we want our component_name to be unique thus we use the count of documents to get the next component name
        component_count = await db.components.count_documents({})
        # we append C to the str(count) to build the entire component name
        component_name = 'C'+str(component_count + 1)
        component.name = component_name
        encoded_component = jsonable_encoder(component)
        new_component = await db.components.insert_one(encoded_component)
        created_component = await db.components.find_one({'_id': new_component.inserted_id})
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_component)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'You are not authorized to add new components')


# get a list of all the components
@router.get('/list', response_model=List[ComponentShowModel], response_description='List all components')
async def list_all_components(current_user: ShowUserModel = Depends(get_current_user)):
    if current_user['role'] == 'producer' or current_user['role'] == 'manager':
        components = await db['components'].find().to_list(1000)
        return components
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'You are not authorized view component data')

# update a component based on the specific id
@router.put('/update/{component_id}', response_description='Modify Existing Component Data', response_model=ComponentShowModel)
async def modify_component_data(component_id: str, component: ComponentUpdateProducerModel, current_user: ShowUserModel = Depends(get_current_user)):
    if current_user['role'] == 'producer' or current_user['role'] == 'manager':
        component = {k: v for k,v in component.dict().items() if v is not None}
        if len(component) >= 1:
            update_result = await db['components'].update_one({'_id': component_id}, {'$set': component})
            if update_result.modified_count == 1:
                    if (updated_component := await db['components'].find_one({'_id': component_id})) is not None:
                        return updated_component
                    if (existing_component := await db['components'].find_one({'_id': component_id})) is not None:
                        return existing_component

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Component with id: {component_id} not found')
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'You are not authorized modify component data')



# delete components based on a specific id
@router.delete('/delete/{component_id}', response_description='Delete a component')
async def delete_device(component_id: str, current_user: ShowUserModel = Depends(get_current_user)):
    if current_user['role'] == 'producer' or current_user['role'] == 'manager':
        delete_result = await db['components'].delete_one({'_id': component_id})

        if delete_result.deleted_count == 1:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Component with id: {component_id} not found')
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'You are not authorized to delete component data')
