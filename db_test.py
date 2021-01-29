from datetime import datetime
from dbhelper import DBHelper


db = DBHelper()

db.setup()
# db.add_item("Wash some clothes.")
# db.add_item("Code some more.")
# db.add_item("Go to their Bernice house.")
# a = db.get_specific_date(1605826800)
# print(db.get_specific_date(1605826800))
#
# print(len(db.get_specific_date(1605826800)))
#
# print(datetime.utcfromtimestamp(a[1][2]).strftime("%d/%m/%Y"))

current_timestamp = datetime.now().replace(hour=0, minute=0, second=0).timestamp()
due_tasks = db.get_specific_date(current_timestamp)
print(due_tasks)
print(current_timestamp)

# db.delete_table()
