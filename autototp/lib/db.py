import sqlite3
from typing import Any, Dict

from uuid import UUID

from pydantic import BaseModel

from autototp.lib.util import logged

DB_URI = 'file:totp.sq3'
TABLES = {
    'User': (
        'id Blob Not Null Primary Key, '
        'name Varchar(128) Not Null Unique, '
        'created Datetime Not Null Default Current_Timestamp'
    ),
    'Input': (
        'id Blob Not Null Primary Key, '
        'userId Blob Not Null, '
        'url Varchar(2048) Not Null, '
        'field Varchar(255) Not Null, '
        'secret Varchar(128) Not Null, '
        'created Datetime Not Null Default Current_Timestamp'
    ),
}


def _adaptUuid4(uuid: UUID):
    return uuid.bytes


def initializedDatabase(uri: str, tableDefs: Dict[str, Any]) -> sqlite3.Connection:
    sqlite3.register_adapter(UUID, _adaptUuid4)
    db = sqlite3.connect(uri, uri=True, detect_types=sqlite3.PARSE_DECLTYPES)
    tables = set(r[0] for r in db.execute('''Select tbl_name From sqlite_master Where type='table' '''))
    for table, tableDef in tableDefs.items():
        if table not in tables:
            db.execute(f'''Create Table {table} ({tableDef})''')
    return db


def create(entity: BaseModel):
    """
    Create database row

    Args:
        entity (BaseModel): Model
    """
    with db as conn:
        dataDict = entity.dict()
        conn.execute(
            f"""
            Insert
            Into {entity.__class__.__name__} ({', '.join(f"{n}" for n in dataDict.keys())})
            Values ({', '.join(f":{n}" for n in dataDict.keys())})
            """,
            logged(f'{entity.__class__.__name__} created', dataDict),
        )
    return entity


db = initializedDatabase(DB_URI, TABLES)
