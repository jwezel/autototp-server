import sqlite3
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(debug=True)
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLITE_MESSAGE_MAPPING = {"NOT NULL constraint failed": "Field required", "UNIQUE constraint failed": "Already existing"}


@app.exception_handler(sqlite3.IntegrityError)
async def unicorn_exception_handler(request: Request, exc: sqlite3.IntegrityError):
    message = ', '.join(str(p) for p in exc.args)
    error, sep, description = message.partition(': ')
    if sep and error in SQLITE_MESSAGE_MAPPING:
        message = f"{SQLITE_MESSAGE_MAPPING[error]}: {description}"
    return JSONResponse(
        status_code=400,
        content={"detail": message},
    )
