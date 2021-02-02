import sqlite3


class DBHelper:

    def __init__(self, dbname='help.sqlite'):
        self.dbname = dbname
        self.conn = sqlite3.connect(self.dbname, check_same_thread=False)

    def setup(self):
        stmt = """
        CREATE TABLE IF NOT EXISTS Todo (id INTEGER PRIMARY KEY, user_id INTEGER, 
        description TEXT, deadline INTEGER);
        CREATE TABLE IF NOT EXISTS Alert (id INTEGER PRIMARY KEY, message_id INTEGER, sent INTEGER);
        """
        self.conn.executescript(stmt)
        self.conn.commit()

    def add_item(self, user_id, item_text, deadline):
        stmt = f"""
        INSERT INTO Todo (user_id, description, deadline) VALUES (?, ?, ?)
        """
        args = (user_id, item_text, deadline)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, user_id, item_text):
        stmt = "DELETE FROM Todo WHERE (user_id, description) = (?, ?)"
        args = (user_id, item_text)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self, user_id):
        args = (user_id,)
        stmt = "SELECT id, description, deadline FROM Todo WHERE user_id=(?)"
        items = self.conn.execute(stmt, args)
        return [todo for todo in items]

    def update_item(self, text_id, new_text, new_deadline):
        stmt = "UPDATE Todo SET description=(?), deadline=(?) WHERE id=(?)"
        args = (new_text, new_deadline, text_id)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_specific_date(self, date):
        stmt = "SELECT user_id, description, deadline, id FROM Todo WHERE deadline<=(?)"
        args = (date,)
        deadline_reached = self.conn.execute(stmt, args)
        return [tasks for tasks in deadline_reached]

    def add_todo_id(self, item_id):
        stmt = "INSERT INTO Alert (message_id, sent) VALUES (?, 1)"
        args = (item_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_sent_list(self, message_id):
        stmt = "SELECT message_id FROM Alert where message_id=(?)"
        args = (message_id,)
        values = self.conn.execute(stmt, args)
        return [value for value in values]

    def del_from_sent_list(self, message_id):
        stmt = "DELETE FROM Alert WHERE message_id=(?)"
        args = (message_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()
