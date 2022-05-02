from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional

# validate out _id field
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')

        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# user model
class UserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr = Field(...)
    name: str = Field(...)
    role: str = Field(...)
    is_active: bool = True
    created_at : Optional[str] = None
    last_login: str
    password: str

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example":{
                "email": "alice@gmail.com",
                "name": "Alice",
                "role": "producer",
                "is_active": "false",
                "created_at": "datetime",
                "last_login": "datetime",
                "password": "fakepassword",
            }
        }

    # validations to check the users being created
    @validator('role')
    def role_is_valid(cls, role: Optional[str]) -> Optional[str]:
        allowed_set = {"manager", "producer", "assembler"}
        if role not in allowed_set:
            raise ValueError(f'Role must be in {allowed_set}, got {role}')
        return role

# this is used to return data; we avoid returning passwords
class UserResponseModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr = Field(...)
    name: str = Field(...)
    role: str = Field(...)
    is_active: bool = True
    created_at : Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example":{
                "email": "alice@gmail.com",
                "name": "Alice",
                "role": "producer",
                "is_active": "false",
                "created_at": "datetime",
                "last_login": "datetime",
            }
        }


 # this updates a user
class UpdateUserModel(BaseModel):
    email: Optional[EmailStr]
    name: Optional[str]
    role: Optional[str]
    is_active: Optional[str]
    created_at: Optional[str]
    last_login: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "alice@gmail.com",
                "name": "Alice",
                "role": "producer",
                "id_active": "false",
                "created_at": "datetime",
                "last_login": "datetime",
            }
        }

# this shows user data
class ShowUserModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: Optional[EmailStr]
    name: Optional[str]
    role: Optional[str]
    is_active: Optional[str]
    created_at: Optional[str]
    last_login: Optional[str]


    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "alice@gmail.com",
                "name": "Alice",
                "role": "producer",
                "created_at": "datetime",
                "last_login": "datetime",
            }
        }



# factory models

# component model and schema
class ComponentModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: Optional[str]
    type: Optional[str]
    quality: Optional[str]
    status: Optional[str]
    location: Optional[str]

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "name": "C1",
                "type": "A",
                "quality": "null",
                "status": "manufactured",
                "location": "producer",
            }
        }

    # validate type of component
    @validator('type')
    def type_is_valid(cls, component_type: Optional[str]) -> Optional[str]:
        allowed_set = {'A', 'B', 'C', 'D', 'E'}
        if component_type not in allowed_set:
            raise ValueError(f'Component type must be in {allowed_set}, got {component_type}')
        return component_type

    # validate location of component
    @validator('location')
    def location_is_valid(cls, location: Optional[str]) -> Optional[str]:
        if location != 'producer':
            raise ValueError(f'Location must be producer got {location}')
        return location
    
    # validate quality, set to null at producer then updated at assembler
    @validator('quality')
    def quality_is_valid(cls, quality: Optional[str]) -> Optional[str]:
        if quality != 'null':
            raise ValueError(f'Quality must be null, got {quality}')
        return quality
    
    # validate status of the of the component
    @validator('status')
    def status_is_valid(cls, status: Optional[str]) -> Optional[str]:
        allowed_set = {'manufactured', 'reviewed'}
        if status not in allowed_set:
            raise ValueError(f'Status must be in {allowed_set}, got {status}')
        return status


# model/schema to update the existing components; we need this at the assembler to change status and quality
class ComponentUpdateModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: Optional[str]
    type: Optional[str]
    quality: Optional[str]
    status: Optional[str]
    location: Optional[str]

    class Config:
        json_encoders = {ObjectId: str}   
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "name": "C1",
                "type": "A",
                "quality": "A",
                "status": "assembled",
                "location": "assembler",
            }
        }

    # validate type of component
    @validator('type')
    def type_is_valid(cls, component_type: Optional[str]) -> Optional[str]:
        allowed_set = {'A', 'B', 'C', 'D', 'E'}
        if component_type not in allowed_set:
            raise ValueError(f'Component type must be in {allowed_set}, got {component_type}')
        return component_type

    # validate location default; at assembler now
    @validator('location')
    def location_is_valid(cls, location: Optional[str]) -> Optional[str]:
        if location != 'assembler':
            raise ValueError(f'Location must be assembler, got {location}')
        return location
    
    # validate quality options
    @validator('quality')
    def quality_is_valid(cls, quality: Optional[str]) -> Optional[str]:
        allowed_set = {'A', 'B', 'C', 'D', 'F'}
        if quality not in allowed_set:
            raise ValueError(f'Quality must be in {allowed_set}, got {quality}')
        return quality
    

    # validate status of the component
    @validator('status')
    def status_is_valid(cls, status: Optional[str]) -> Optional[str]:
        allowed_set = {'assembled', 'rejected'}
        if status not in allowed_set:
            raise ValueError(f'Status must be in {allowed_set}, got {status}')
        return status


# model/schema to show component data
class ComponentShowModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: Optional[str]
    type: Optional[str]
    quality: Optional[str]
    status: Optional[str]
    location: Optional[str]

    class Config:
        json_encoders = {ObjectId: str}   
        schema_extra = {
            "example": {
                "name": "C1",
                "type": "A",
                "quality": "A",
                "status": "assembled",
                "location": "assembler",
            }
        }



# devices

# device schema
class DeviceModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: Optional[str]
    component_1: Optional[str]
    component_2: Optional[str]

    class Config:
        json_encoders = {ObjectId: str}   
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "name": "D1",
                "component_1": "A",
                "component_2": "B"
            }
        }
    # validate data given as the first component
    @validator('component_1')
    def component_1_is_valid(cls, component_1: Optional[str]) -> Optional[str]:
        allowed_set = {'A', 'C'}
        if component_1 not in allowed_set:
            raise ValueError(f'component_1 must be in {allowed_set}, got {component_1}')
        return component_1
    
    # validate data given as the second component
    @validator('component_2')
    def component_2_is_valid(cls, component_2: Optional[str]) -> Optional[str]:
        allowed_set = {'B', 'C', 'E'}
        if component_2 not in allowed_set:
            raise ValueError(f'component_2 must be in {allowed_set}, got {component_2}')
        return component_2



# model/schema to show devices
class DeviceShowModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: Optional[str]
    component_1: Optional[str]
    component_2: Optional[str]

    class Config:
        json_encoders = {ObjectId: str}   
        schema_extra = {
            "example": {
                "name": "D1",
                "component_1": "A",
                "component_2": "B"
            }
        }
    
