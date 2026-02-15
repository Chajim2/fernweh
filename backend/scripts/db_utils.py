from flask import g
import pysqlite3 as sqlite3
import importlib.resources


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect('database.db',
                                detect_types=sqlite3.PARSE_DECLTYPES)
        # load sqlite-vector 
        ext_path = importlib.resources.files("sqlite_vector.binaries") / "vector"
        g.db.enable_load_extension(True)
        g.db.load_extension(str(ext_path))
        g.db.enable_load_extension(False)

        cursor = g.db.cursor()
        cursor.execute("SELECT vector_init('vector_chunks'," \
                                          "'embedding'," \
                                          "'type=FLOAT32,dimension=768')")
    return g.db
