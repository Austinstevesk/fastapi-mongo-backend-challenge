from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response

from ..models import ComponentUpdateModel, DeviceModel,  DeviceShowModel
from ..settings import client

from ..models import ShowUserModel
from ..dependencies import get_current_user

from .producer import  db as producer_db
db = client.devices


router = APIRouter(
    tags=['assembler'],
    prefix='/assembler'
)

# @router.put('/update/{component_name}', response_description='Update Component data')
# async def update_component_on_assembler(component: ComponentUpdateModel):
#     pass


# update component data to ensure we update the quality, status and location
@router.put('/update/components/{component_id}', response_model=ComponentUpdateModel, response_description='Update Components: Include quality and status')
async def update_components(component_id: str, component: ComponentUpdateModel, current_user: ShowUserModel = Depends(get_current_user)):
    if current_user['role'] == 'assembler' or current_user['role'] == 'manager':
        component = {k: v for k,v in component.dict().items() if v is not None}
        if len(component) >= 1:
            update_result = await producer_db['components'].update_one({'_id': component_id}, {'$set': component})
            await producer_db['components'].update_one({'_id': component_id}, {'$set':{'location': 'assembler'}})
            if update_result.modified_count == 1:
                    if (updated_component := await producer_db['components'].find_one({'_id': component_id})) is not None:
                        return updated_component
                    if (existing_component := await producer_db['components'].find_one({'_id': component_id})) is not None:
                        return existing_component

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Component with id: {component_id} not found')
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'You are not authorized to modify device data')



# add a new device to the device document
@router.post('/add', response_model=DeviceShowModel, response_description='Create a new device')
async def create_new_device(device: DeviceModel, current_user: ShowUserModel = Depends(get_current_user)):
    if current_user['role'] == 'assembler' or current_user['role'] == 'manager':
        component_1 = await producer_db['components'].find_one({'type': device.component_1})
        component_2 = await producer_db['components'].find_one({'type': device.component_2})
        if component_1 is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Component with type {device.component_1} not found')
        if component_2 is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Component with type {device.component_2} not found')
        if component_1['quality'] == 'null':
            raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT,
                                detail=f'Component {device.component_1} has not been reviewed and assigned quality at the assembler')

        if component_2['quality'] == 'null':
            raise HTTPException(status_code=status.HTTP_206_PARTIAL_CONTENT,
                                detail=f'Component {device.component_2} has not been reviewed and assigned quality')
        
        if component_1['quality'] == 'D' and component_1.type == 'A':
            await producer_db['components'].update_one({'_id': component_1.id}, {'$set': {'status': 'rejected'}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'Component {device.components[0]} rejected')
        if component_1['quality'] == 'F' and component_2['quality'] == 'F':
            await producer_db['components'].update_one({'_id': component_2.id}, {'$set': {'status': 'rejected'}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'Both components rejected')
        if component_1 == "A" and component_2 == "B":
            device.name = 'D1'
        if component_1 == "C" and component_2 == "D":
            device.name = 'D2'

        if component_1 == "A" and component_2 == "E":
            device.name = 'D3'


        encoded_device = jsonable_encoder(device)
        new_device = await db.devices.insert_one(encoded_device)
        created_device = await db.devices.find_one({'_id': new_device.inserted_id})


        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_device)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'You are not authorized to add new devices')


# get a list of all devices
@router.get('/list', response_model=List[DeviceShowModel], response_description='Show all devices')
async def get_all_devices(current_user: ShowUserModel = Depends(get_current_user)):
    if current_user['role'] == 'assembler' or current_user['role'] == 'manager':
        devices = await db.devices.find().to_list(1000)
        return devices
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'You are not authorized view device data')

# update a device based on the id
@router.put('/update/devices/{device_id}', response_model=DeviceShowModel, response_description='Modify existing device data')
async def update_device_data(device_id: str, device: DeviceModel, current_user: ShowUserModel = Depends(get_current_user)):
    if current_user['role'] == 'assembler' or current_user['role'] == 'manager':
        device = {k: v for k,v in device.dict().items() if v is not None}
        if len(device) >= 1:
            update_result = await db['devices'].update_one({'_id': device_id}, {'$set': device})
            if update_result.modified_count == 1:
                    if (updated_device := await db['devices'].find_one({'_id': device_id})) is not None:
                        return updated_device
                    if (existing_device := await db['devices'].find_one({'_id': device_id})) is not None:
                        return existing_device

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Device with id: {device_id} not found')
    else:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'You are not authorized modify device data')

# delete a device using a soecific id
@router.delete('/delete/{device_id}', response_description='Delete a component')
async def delete_device(device_id: str, current_user: ShowUserModel = Depends(get_current_user)):
    if current_user['role'] == 'assembler' or current_user['role'] == 'manager':
        delete_result = await db['devices'].delete_one({'_id': device_id})
        if delete_result.deleted_count == 1:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Component with id: {device_id} not found')
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'You are not authorized to delete device data')