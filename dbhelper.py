import sqlite3
from datetime import timedelta, datetime


class DBHelper:

    def __init__(self, dbname='help.sqlite'):
        self.dbname = dbname
        self.conn = sqlite3.connect(self.dbname, check_same_thread=False)

    def setup(self):
        stmt = """
        CREATE TABLE IF NOT EXISTS Todo (id INTEGER, 
        description TEXT, deadline INTEGER)
        """
        self.conn.execute(stmt)
        self.conn.commit()

    def add_item(self, user_id, item_text, deadline):
        stmt = f"""
        INSERT INTO Todo (id, description, deadline) VALUES (?, ?, ?)
        """
        args = (user_id, item_text, deadline)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, user_id, item_text):
        stmt = "DELETE FROM Todo WHERE (id, description) = (?, ?)"
        args = (user_id, item_text)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self, user_id):
        args = (user_id,)
        stmt = "SELECT description, deadline FROM Todo WHERE id=(?)"
        items = self.conn.execute(stmt, args)
        return [todo for todo in items]

    def update_item(self, user_id, item_text, new_text):
        stmt = "UPDATE Todo SET description=(?), deadline=30 WHERE id, description=(?, ?)"
        args = (new_text, user_id, item_text)
        self.conn.execute(stmt, args)
        self.conn.commit()

    # def delete_table(self):
    #     stmt = "DROP TABLE Todo"
    #     try:
    #         self.conn.execute(stmt)
    #         self.conn.commit()
    #     except sqlite3.OperationalError as e:
    #         return e
