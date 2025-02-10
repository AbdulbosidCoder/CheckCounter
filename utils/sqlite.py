import sqlite3
from datetime import datetime


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parametrs: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parametrs:
            parametrs = ()
        with self.connection as connection:
            cursor = connection.cursor()
            data = None
            cursor.execute(sql, parametrs)

            if commit:
                connection.commit()
            if fetchall:
                data = cursor.fetchall()
            if fetchone:
                data = cursor.fetchone()
            return data

    def create_table_users(self):
        sql = """
        CREATE TABLE Users(
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER,
            status text,
            role text,
            name text 
            ); 
            """
        self.execute(sql, commit=True)

    def create_table_pictures(self):
        sql = """
        CREATE TABLE Pictures(
        id INTEGER PRIMARY KEY,
        image_url text,
        created_at datetime,
        created_by integer,
        name text
        );
        """
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += "AND ".join([
            f"{item}=?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, telegram_id: int, status: str, role: str, name: str):
        sql = """INSERT INTO Users(telegram_id, status, role, name)
        VALUES(?, ?, ?, ? )"""

        self.execute(sql, parametrs=(telegram_id, status, role, name), commit=True)


    def add_picture(self, image_url: str, created_at: datetime, created_by, name):
        sql = """INSERT INTO Pictures(image_url, created_at, created_by, name) 
        VALUES(?, ?, ?, ? )"""

        self.execute(sql, parametrs=(image_url, created_at, created_by, name), commit=True)

    def get_pic_by_user_id(self, telegram_id):
        sql = """SELECT * FROM Pictures WHERE created_by = ?"""

        return self.execute(sql, parametrs=(telegram_id,), fetchall=True)

    def get_pic_by_id(self,telegram_id):
        sql = """SELECT * FROM Pictures WHERE created_by = ? ORDER BY id """
        return self.execute(sql, parametrs=(telegram_id,), fetchall=True)

    def get_pic_by_name(self,telegram_id, name):
        sql = """SELECT * FROM Pictures WHERE name = ? and created_by = ? ORDER BY id """
        return self.execute(sql, parametrs=(telegram_id,), fetchall=True)

    def update_picture(self, image_url, created_by, name):
        sql = """UPDATE Pictures 
                 SET name = ? 
                 WHERE created_by = ? AND image_url = ?"""
        self.execute(sql, parametrs=(name, created_by, image_url), commit=True)

    def select_pictures_names(self, telegram_id):
        sql = """SELECT name FROM Pictures WHERE created_by = ? ORDER BY id"""
        return self.execute(sql, parametrs=(telegram_id,), fetchall=True)

    def get_clients_history(self, telegram_id):
        sql = """
        SELECT DISTINCT name 
        FROM Pictures 
        WHERE created_by = ? 
        ORDER BY id DESC
        """
        return self.execute(sql, parametrs=(telegram_id, ), fetchall=True)

    def get_all_clients(self,telegram_id):
        sql = """SELECT image_url FROM Pictures where created_by = ? ORDER BY id DESC """
        return self.execute(sql, parametrs=(telegram_id,), fetchall=True)

    def delete_all_clients(self, telegram_id):
        sql =  """DELETE FROM Pictures WHERE created_by = ? """

        self.execute(sql, parametrs=(telegram_id,), commit=True)

    def delete_clints_history(self, telegram_id, name):
        sql = """DELETE FROM Pictures WHERE name = ? AND created_by = ? """
        self.execute(sql, parametrs=(name,telegram_id,), commit=True)


