import sqlite3

# Conecta a la base de datos
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

# Muestra todo lo que hay en la tabla usuarios
cursor.execute("SELECT * FROM usuarios")
usuarios = cursor.fetchall()

# Imprime resultados
for usuario in usuarios:
    print(usuario)

conn.close()
