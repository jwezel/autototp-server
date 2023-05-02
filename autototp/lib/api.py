from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import Header, HTTPException, Response
from pydantic import UUID4, BaseModel, Field
from pyotp import TOTP

from .app import app
from .db import create, db
from .util import logged, logger


class DatabaseModel(BaseModel):
    id: UUID4 = Field(default_factory=lambda: uuid4())
    created: datetime = Field(default_factory=datetime.now)


class Input(DatabaseModel):
    userId: UUID4
    url: Optional[str]  # In /api/v1/input not passed in body but in header Origin
    field: str
    secret: Optional[str]


class InputBody(BaseModel):
    user: str
    field: str
    secret: Optional[str]


class InputResponse(BaseModel):
    code: Optional[str] = Field(default=None)


@app.post('/api/v1/input')
async def post_input(input: Input, origin: str = Header()) -> InputResponse:
    result = InputResponse()
    with db as conn:
        secrets = conn.execute(
            '''
            Select
                I.secret
            From
                User U Left Join Input I On U.id = I.userId
            Where
                url = :url And
                field = :field And
                U.id = :userId
            Order By
                I.created Desc
            ''',
            vars(input) | dict(url=origin),
        )
        secretRows = secrets.fetchone()
        if secretRows and len(secretRows) > 0:
            secret = logged('Secret fetched', secretRows)[0]
        else:
            logger.debug({'Input rows': secretRows})
            secret = None
        if input.secret and not secret:
            input.url = origin
            create(input)
            secret = input.secret
        if secret:
            try:
                otpgen = TOTP(secret)
                result.code = otpgen.now()
            except BaseException as e:
                raise HTTPException(status_code=400, detail=f'TOTP secret: {e}')
        return logged('Returned', result)


class User(DatabaseModel):
    name: str


class UserCreateRequestBody(BaseModel):
    name: str


@app.post('/api/v1/user')
async def post_user(user: User, apiResponse: Response) -> User:
    with db as conn:
        userDict = user.dict()
        conn.execute(
            f"""
            Insert
            Into User ({', '.join(f"{n}" for n in userDict.keys())})
            Values ({', '.join(f":{n}" for n in userDict.keys())})
            """,
            logged('User created', userDict),
        )
    apiResponse.status_code = 201
    return user


class UserDeleteRequestBody(BaseModel):
    id: UUID4


@app.delete('/api/v1/user')
async def delete_user(body: UserDeleteRequestBody):
    with db as conn:
        cursor = conn.execute(
            'Delete From User Where id = :id',
            logged('User deleted', body.dict()),
        )
        if cursor.rowcount < 1:
            raise HTTPException(404, "Not found")
