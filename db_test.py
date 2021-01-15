from dbhelper import DBHelper


db = DBHelper()

db.setup()
# db.add_item("Wash some clothes.")
# db.add_item("Code some more.")
# db.add_item("Go to their Bernice house.")

print(db.get_items(656785956)[:4])

db.update_item(656785956, "Read some telegram stuff", 12434567, "Read some django stuff")

print(db.get_items(656785956))

# db.delete_table()
