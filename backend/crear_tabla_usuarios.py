import sqlite3

# Conecta a la base de datos
conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

# Crea la tabla si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    contraseña TEXT NOT NULL,
    rol TEXT DEFAULT 'usuario'
)
''')

# Agrega un usuario de prueba
cursor.execute("INSERT INTO usuarios (usuario, contraseña, rol) VALUES (?, ?, ?)",
               ("juanito", "1234", "admin"))

conn.commit()
conn.close()

print("✅ Tabla creada y usuario insertado")
