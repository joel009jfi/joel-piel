import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
cnx = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'joel_piel')
)
cursor = cnx.cursor()
cursor.execute("SELECT Id_pedido, metodo_pago FROM pedidos WHERE metodo_pago = 'Completo'")
rows = cursor.fetchall()
print(f"Ordenes con 'Completo': {len(rows)}")
for r in rows:
    print(f"  Pedido {r[0]}: {r[1]}")
if rows:
    cursor.execute("UPDATE pedidos SET metodo_pago = 'Pagado' WHERE metodo_pago = 'Completo'")
    cnx.commit()
    print(f"Actualizadas {cursor.rowcount} ordenes")
else:
    print("No hay ordenes con 'Completo'")
cursor.close()
cnx.close()
