from re import split
from flask import Flask, jsonify,request
from flask_cors import CORS
import json
app = Flask(__name__)
CORS(app)

import pyodbc

# Configura tus propios valores de conexión
server = 'server-asso.database.windows.net'  # El nombre de tu servidor
database = 'GymDB'  # El nombre de tu base de datos
username = 'Dylan'
password = 'Asso-12345'
driver = '{ODBC Driver 17 for SQL Server}'  # El driver que estás utilizando

# Crea la cadena de conexión
connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

# Crea la conexión
cnxn = pyodbc.connect(connection_string)

"""
get-obtener info de la bdGraa
post-crear info en la bd
put-actualizar info en la bd
delete-borrar de la bd
"""

@app.route("/")
#definimos el metodo para root
def root():
    return "Raiz"











# Endpoint DELETE para eliminar una rutina por ID de usuario y devolverla como JSON
@app.route('/rutinas/<id_usuario>', methods=['DELETE'])
def eliminar_rutina(id_usuario):
    cursor = cnxn.cursor()
    # Recupera la rutina antes de eliminarla
    cursor.execute("SELECT * FROM rutinas WHERE id_usuario=?", int(id_usuario))
    rutina = cursor.fetchone()

    if rutina:
        # Recupera los elementos de la tabla rutina_ejercicio asociados a la rutina eliminada
        cursor.execute("SELECT * FROM rutina_ejercicio WHERE id_rutina=?", rutina.id_rutina)
        ejercicios_rutina = cursor.fetchall()
        ejercicios=extraer_ejercicios(ejercicios_rutina)
        # Guarda la rutina antes de eliminarla
        rutina_guardada = {
            'id_rutina': rutina.id_rutina,
            'nombre': rutina.nombre,
            'id_usuario': rutina.id_usuario,
            'ejercicios':ejercicios,
            'fecha_inicio': rutina.fecha_inicio.strftime("%d/%m/%Y"),
            'duracion': rutina.duracion,
        }

        print("lista:")
        print(rutina_guardada)


        # Realiza la operación de eliminación en la tabla pivote
        cursor.execute("DELETE FROM rutina_ejercicio WHERE id_rutina=?", rutina.id_rutina)
        cnxn.commit()
        # Realiza la operación de eliminación en tabla de rutinas
        cursor.execute("DELETE FROM rutinas WHERE id_usuario=?", int(id_usuario))
        cnxn.commit()

        return jsonify(rutina_guardada), 200
    else:
        return jsonify({"mensaje": "Rutina no encontrada"}), 404

def extraer_ejercicios(lista):
    resultado=""
    for i in range(len(lista)):
        resultado+=str(lista[i][1])+","
    return resultado[0:len(resultado)-1]




















# Ruta para obtener información de ejercicios
@app.route('/ejercicios', methods=['GET'])
def obtener_ejercicios():
    # Obtener la lista de IDs proporcionados en la solicitud
    ids_solicitud = request.args.getlist('ids')
    ids_solicitud = ids_solicitud[0].split(',')
    ids_solicitud = ','.join(map(str, ids_solicitud))
    print("idsolicitud->>>",ids_solicitud)
    # Construye una cadena de marcadores de posición para los IDs
    cursor = cnxn.cursor()
    
    print("===================================")
    print("RECIBI: ", ids_solicitud)
    print("===================================")

    # Si no se proporciona ningún ID, devolver todos los ejercicios
    if not ids_solicitud:
        cursor.execute("SELECT * FROM ejercicios")
        rows = cursor.fetchall()
        ejercicios = []
        for row in rows:
            ejercicio = {
                'id_ejercicio': row.id_ejercicio,  
                'tren': row.tren,  
                'musculo': row.musculo,  
                'nombre': row.nombre,  
                'foto': row.foto
            }
            ejercicios.append(ejercicio)

        print("===================================")
        print("ENVIANDO TODOS LOS REGISTROS")
        print("===================================")
        return jsonify(ejercicios)

    # Filtrar los ejercicios cuyos IDs no están en la lista proporcionada
    cursor.execute("SELECT * FROM ejercicios WHERE id_ejercicio NOT IN ({})".format(ids_solicitud))
    rows = cursor.fetchall()
    ejercicios_filtrados = []
    for row in rows:
        ejercicio_filtrado = {
            'id_ejercicio': row.id_ejercicio,  
            'tren': row.tren,  
            'musculo': row.musculo,  
            'nombre': row.nombre,  
            'foto': row.foto
        }
        ejercicios_filtrados.append(ejercicio_filtrado)

    print("===================================")
    print("EJERCICIOS FILTRADOS:", ejercicios_filtrados)
    print("===================================")
    return jsonify(ejercicios_filtrados)








# Endpoint para obtener información de usuarios
@app.route('/users', methods=['GET'])
def get_usuario():
    # Este comando obtiene la información que nos mandaron (como por postman)
    id_usuario = request.args.get('id_usuario')
    # Crea un cursor a partir de la conexión
    cursor = cnxn.cursor()

    if id_usuario is not None:
        if id_usuario == "0":
            # Si no se proporciona 'id_usuario', devuelve información de todos los usuarios
            cursor.execute("SELECT * FROM usuarios")
            rows = cursor.fetchall()
            usuarios = []
            for row in rows:
                usuario = {
                    'id_usuario': row.id_usuario, 
                    'nombre': row.nombre,
                    'fecha_registro': row.fecha_registro 
                }
                usuarios.append(usuario)
            return jsonify(usuarios), 200
        else:
            # Si se proporciona un 'id_usuario', devuelve información del usuario específico
            cursor.execute("SELECT * FROM usuarios WHERE id_usuario=?", int(id_usuario))
            row = cursor.fetchone()
            if row:
                usuario = {
                    'id_usuario': row.id_usuario, 
                    'nombre': row.nombre,
                    'fecha_registro': row.fecha_registro 
                }
                return jsonify(usuario), 200
            else:
                return jsonify({"mensaje": "Usuario no encontrado"}), 404











@app.route("/users",methods=['POST'])
def create_user():
    #este comando obtiene la informacion que nos mandaron (como por postman)
    data=request.get_json()

    # Crea un cursor a partir de la conexión
    cursor = cnxn.cursor()
    # Crea la consulta SQL para insertar los datos
    sql = """
    INSERT INTO usuarios (nombre, fecha_registro)
    VALUES (?, ?)
    """
    # Ejecuta la consulta SQL
    cursor.execute(sql, data['name'], data['date'])
    # Confirma la transacción
    cnxn.commit()

    print("===================================")
    print("Guardar en la BD.")
    print("nombre:",data["name"])
    print("fecha:",data["date"])
    print("===================================")
    return jsonify(data),201

if __name__ == "__main__":
    app.run(debug=True)
