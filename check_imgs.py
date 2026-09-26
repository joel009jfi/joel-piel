import mysql.connector
conn = mysql.connector.connect(host="localhost", user="root", password="", database="joel_piel")
c = conn.cursor()
c.execute("SELECT id_producto, nombre, imagen_url FROM productos")
for r in c.fetchall():
    print(f"ID {r[0]}: {r[1]} -> {r[2]}")
conn.close()
