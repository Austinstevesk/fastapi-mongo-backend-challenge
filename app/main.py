from cgitb import handler
from fastapi import FastAPI


from .src.routers.users import router as user_router
from .src.routers.auth import router as auth_router
from .src.routers.producer import router as producer_router
from .src.routers.assembler import router as assembler_router

from mangum import Mangum
# create an app using FastAPI class
app = FastAPI()
# include other routers


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(producer_router)
app.include_router(assembler_router)

# default root to make sure we do not have an error when we access '/'
@app.get('/', response_description='Root')
async def root():
    return {"Message": "Welcome Backend Developer. Head over to '/docs' to view available endpoints"}

handler = Mangum(app)