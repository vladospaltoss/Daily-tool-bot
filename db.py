import sqlite3
import pathlib
import sys

class Datebase:
    def __init__(self, db_file) -> None:
        script_path = pathlib.Path(sys.argv[0]).parent
        self.conection = sqlite3.connect(script_path / "database.db")
        self.cursor = self.conection.cursor()

    def user_exists(self, user_id):
        with self.conection:
            res = self.cursor.execute('SELECT * FROM "users" WHERE "user_id" = ?', (user_id,)).fetchmany(1)
            return bool(len(res))

    def add_user(self, user_id):
        with self.conection:
            return self.cursor.execute('INSERT INTO "users" ("user_id") VALUES (?)', (user_id,))

    def set_active(self, user_id, active):
        with self.conection:
            return self.cursor.execute('UPDATE "users" SET "active" = ? WHERE "user_id" = ?', (active, user_id,))
    
    def get_users(self):
        with self.conection:
            return self.cursor.execute('SELECT "user_id", "active" FROM "users"').fetchall()






