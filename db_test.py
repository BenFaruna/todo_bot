from dbhelper import DBHelper


db = DBHelper()

db.setup()
# db.add_item("Wash some clothes.")
# db.add_item("Code some more.")
# db.add_item("Go to their Bernice house.")

print(db.get_items())

# db.update_item("Wash some clothes.", "Love yourself.")

# print(db.get_items())

# db.delete_table()
