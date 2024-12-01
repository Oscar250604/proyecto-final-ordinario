from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret_key_for_session"  # Para manejar flashes de mensaje

# Conectar a la base de datos
def conectar_db():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ferreteria"
        )
        return conexion
    except mysql.connector.Error as err:
        flash(f"Error al conectar a la base de datos: {err}", "danger")
        return None


@app.route('/')
def index():
    # Mostrar los productos
    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos")
        productos = cursor.fetchall()
        conexion.close()
    return render_template('index.html', productos=productos)


@app.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio_publico = float(request.form['precio_publico'])
        precio_distribuidor = float(request.form['precio_distribuidor'])
        stock = int(request.form['stock'])

        if nombre and precio_publico > 0 and precio_distribuidor > 0 and stock >= 0:
            conexion = conectar_db()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute(
                    "INSERT INTO productos (nombre, precio_publico, precio_distribuidor, stock) VALUES (%s, %s, %s, %s)",
                    (nombre, precio_publico, precio_distribuidor, stock)
                )
                conexion.commit()
                conexion.close()
            flash("Producto agregado con éxito al inventario", "success")
            return redirect(url_for('index'))
        else:
            flash("Por favor, completa todos los campos correctamente.", "warning")
    return render_template('agregar_producto.html')


@app.route('/editar_producto/<int:id_producto>', methods=['GET', 'POST'])
def editar_producto(id_producto):
    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = %s", (id_producto,))
        producto = cursor.fetchone()
        if not producto:
            flash("Producto no encontrado", "danger")
            return redirect(url_for('index'))

        if request.method == 'POST':
            nombre = request.form['nombre']
            precio_publico = float(request.form['precio_publico'])
            precio_distribuidor = float(request.form['precio_distribuidor'])
            stock = int(request.form['stock'])

            cursor.execute(
                "UPDATE productos SET nombre = %s, precio_publico = %s, precio_distribuidor = %s, stock = %s WHERE id = %s",
                (nombre, precio_publico, precio_distribuidor, stock, id_producto)
            )
            conexion.commit()
            conexion.close()
            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for('index'))

    return render_template('agregar_producto.html', producto=producto)


@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    if request.method == 'POST':
        id_producto = request.form['id_producto']
        cantidad = int(request.form['cantidad'])

        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            cursor.execute("SELECT * FROM productos WHERE id = %s", (id_producto,))
            producto = cursor.fetchone()

            if producto and cantidad > 0 and cantidad <= producto[4]:  # producto[4] es el stock
                total = producto[2] * cantidad  # precio_publico
                new_stock = producto[4] - cantidad  # nuevo stock

                cursor.execute("UPDATE productos SET stock = %s WHERE id = %s", (new_stock, id_producto))
                conexion.commit()
                conexion.close()
                flash(f"Venta realizada. Total: ${total:.2f}", "success")
            else:
                flash("Producto no disponible o cantidad inválida.", "danger")

        return redirect(url_for('ventas'))

    return render_template('ventas.html')


if __name__ == "__main__":
    app.run(debug=True)
