import better_exceptions

better_exceptions.hook()

from typing import Optional
from uuid import uuid4

from fastapi import Header
from pydantic import BaseModel
from pyotp import TOTP

from .app import app
from .db import db
from .util import logged, logger


class InputBody(BaseModel):
    token: str
    field: str
    secret: Optional[str]


@app.post('/api/v1/input')
async def post_input(input: InputBody, origin: str = Header()):
    result = {}
    logger.debug(input)
    with db as conn:
        if input.secret:
            conn.execute(
                'Insert Into Input (id, tokenId, url, field, secret) Values(?, ?, ?, ?, ?)',
                logged('Input created', (uuid4().hex, input.token, origin, input.field, input.secret)),
            )
            secret = input.secret
        else:
            secrets = conn.execute(
                '''
                Select
                    I.secret
                From
                    Token T Left Join Input I On T.id = I.tokenId
                Where
                    url = :url And field = :field And T.id = :token
                Order By
                    I.time Desc
                ''',
                vars(input) | dict(token=input.token, url=origin),
            ).fetchone()
            if secrets:
                secret = logged('Secret fetched', secrets)[0]
            else:
                secret = None
        if secret:
            otpgen = TOTP(secret)
            result['code'] = otpgen.now()
        return logged('Returned', result)


@app.post('/api/v1/user/create')
async def post_user_create():
    with db as conn:
        conn.execute(
            'Insert Into Token (id) Values(?)',
            logged('User created', (uuid4().hex,)),
        )


@app.post('/api/v1/user/delete')
async def post_user_delete(token: str):
    with db as conn:
        conn.execute(
            'Delete From Token Where id = ?',
            logged('User deleted', (token,)),
        )
