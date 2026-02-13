from flask import g
import sqlite3


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect('database.db',
                                detect_types=sqlite3.PARSE_DECLTYPES)

    return g.db
