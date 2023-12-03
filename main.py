from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import contacts, auth, users

app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(contacts.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')


@app.get('/')
def read_root():
    """
    The read_root function returns a dictionary with the key 'message' and value 'Hello'.

    :return: A dictionary
    :doc-author: Trelent
    """
    return {'message': 'Hello'}
