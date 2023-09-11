import sqlite3,sys

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect(sys.argv[1])

conn.row_factory = dict_factory
cur = conn.cursor()

cur.execute("SELECT * FROM ESA")

row= cur.fetchone()


print(row)

print(("key = ", row['exp_raster']))
print(("value = ", row['exp_ds']))
