import sqlite3
from typing import Any, Dict

DB_URI = 'file:totp.sq3'
TABLES = {
    'Token': 'id Char(32) Not Null Primary Key, time Datetime Not Null Default Current_Timestamp',
    'Input': (
        'id Char(32) Not Null Primary Key,'
        'tokenId Char(32) Not Null,'
        'url Varchar(2048) Not Null,'
        'field Varchar(255) Not Null,'
        'secret Varchar(128) Not Null,'
        'time Datetime Not Null Default Current_Timestamp'
    ),
}


def initializedDatabase(uri: str, tableDefs: Dict[str, Any]) -> sqlite3.Connection:
    db = sqlite3.connect(uri, uri=True)
    tables = set(r[0] for r in db.execute('''Select tbl_name From sqlite_master Where type='table' '''))
    for table, tableDef in tableDefs.items():
        if table not in tables:
            db.execute(f'''Create Table {table} ({tableDef})''')
    return db


db = initializedDatabase(DB_URI, TABLES)
