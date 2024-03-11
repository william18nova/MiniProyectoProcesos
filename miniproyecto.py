import json
import os
import time
import datetime
from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://Finchi:Juanjose.123@cluster0.pndlt5o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
FileLog = "log.txt"


# Definición de roles disponibles y variables iniciales
roles = {'cliente', 'trabajador', 'administrador', 'especial'}
tiempo = 1
userID = None
# Nombres de archivos para almacenar datos de usuarios, inventario y ventas
client = MongoClient(uri) 

db = client['Procesos']

inventario = db['inventario']
ventas = db['ventas']
usuarios = db['usuarios']



def verAPUntos():
    global usuarios
    accion = None
    os.system('cls' if os.name == 'nt' else 'clear')
    if( userID["APUntos"] > 1 ):
        print(f'Hola {userID["name"]} Tines: {userID["APUntos"]} puntos')
    else:
        print(f'Hola {userID["name"]} Tines: {userID["APUntos"]} punto')
    input("Presiona cualquier boton para salir")

# Función para realizar una compra
def realizarVenta():
    global usuarios, ventas, inventario
    salidaMenu = None
    carrito = {}

    # Carga de usuarios y ventas desde archivos JSON

    # Proceso de compra, incluyendo selección de cliente, productos, y finalización de compra
    # La lógica involucra interacciones con el usuario a través de la consola
    # Se manejan operaciones como agregar y eliminar productos del carrito, y calcular el total y cambio

    salidaMenu2 = None

    while (salidaMenu2 != 0):

        salidaMenu = None

        time.sleep(tiempo)
        os.system('cls' if os.name == 'nt' else 'clear')  
        print("Si el cliente no esta en la base de datos dejar el campo vacio")
        idComprador = input("ID del cliente: ")

        while (usuarios.find_one({'_id': idComprador}) == None and idComprador != ""):
                
            time.sleep(tiempo)
            os.system('cls' if os.name == 'nt' else 'clear')  
            print("El id no esta en la base de datos")
            idComprador = input("ID del cliente: ")

        fecha_entrada = input("Por favor, ingrese la fecha de la compra en el formato DD-MM-YYYY o no ingrese si es de hoy: ")


        while (salidaMenu != 0):
            
            time.sleep(tiempo)
            os.system('cls' if os.name == 'nt' else 'clear')  

            if (inventario.count_documents({}) > 0):

                if (idComprador != ""):
                    print("Cliente: ", usuarios.find_one({'_id': idComprador})['name'])
                else:
                    print("Cliente: Anonimo")
                    
                for i in carrito:
                    print(i, ' x ', carrito[i]['cantidad'], 'Unidad: ', carrito[i]['unidad'], ' Total: ', carrito[i]['total'])
                
                print(' 1. Agregar producto\n 2. Eliminar producto\n 3. Pagar\n 0. Cancelar compra\n -1. Salir')
                accion = int(input())

                if (accion == 1):

                    item = input('Que producto quieres agregar a la cuenta: ')

                    while (inventario.find_one({'_id': item}) == None):
                        print('el producto no existe')
                        item = input('Que producto quieres agregar a la cuenta: ')

                    item2 = inventario.find_one({'_id': item})

                    print(item, ' Precio: ', item2['precio'])
                    cantidad = int(input('Cantidad: '))

                    while (cantidad > item2['cantidad']):
                        print('No hay suficientes unidades del producto')
                        cantidad = int(input('Cantidad: '))

                    print(cantidad, ' x ', 'item Precio: ', item2['precio'])
                    carrito[item] = {'cantidad': cantidad, 'unidad': item2['precio'], 'total': item2['precio'] * cantidad}
                    
                elif (accion == 2):

                    if (len(carrito) == 0):
                        print('El carrito esta vacio')
                    else:
                        borrarItem = input('Que producto quieres eliminar: ')

                        while (borrarItem not in carrito):
                            print('Este producto no esta en el carrito')
                        
                        del carrito[borrarItem]

                elif (accion == 3):

                    if (len(carrito) == 0):
                        print('El carrito esta vacio')

                    else:
                        total = 0
                        print('Tu factura:')

                        for i in carrito:
                            print(i, ' x ', carrito[i]['cantidad'], 'Unidad: ', carrito[i]['unidad'], ' Total: ', carrito[i]['total'])
                            total += carrito[i]['total']

                        print('Total: ', total)
                        if idComprador != "":
                            print(" 1) Efectivo\n 2) APUntos")
                            metodoPago = int(input("Metodo de pago: "))
                        if metodoPago == 2:
                            comprador = usuarios.find_one({'_id': idComprador})
                            if comprador['APUntos'] * 4 >= total:
                                usuarios.update_one({'_id': idComprador}, {'$set': {'APUntos': comprador['APUntos'] - (total // 4)}})
                                
                                newVenta = {}
                                newVenta['carrito'] = {}

                                for i in carrito:
                                    inventario.update_one({'_id': i}, {'$set': {'cantidad': inventario.find_one({'_id': i})['cantidad'] - carrito[i]['cantidad']}})
                                    newVenta['carrito'][i] = {'cantidad': carrito[i]['cantidad'], 'precio': carrito[i]['unidad']}

                                newVenta['total'] = total
                                newVenta['cambio'] = 0

                                if (fecha_entrada == ""):
                                    newVenta['fecha'] = datetime.datetime.now().strftime("%d-%m-%Y")

                                else:
                                    newVenta['fecha'] = fecha_entrada

                                newVenta['comprador'] = 'Anonimo' if idComprador == "" else {'id': idComprador, 'name': usuarios.find_one({'_id': idComprador})['name']}
                                newVenta['vendedor'] = {'id': userID['_id'], 'name': userID['name']}
                                carrito = {}
                                ventas.insert_one(newVenta)
                                print('!!Compra realizada exitosamente!!')
                                salidaMenu2 = int(input('Presiona 0 para salir o cualquier otro numero para seguir registrando ventas\n'))
                                log(f'{userID["_id"]} realizo una venta a {newVenta["comprador"]} con APUntos por un total de {total}$ el {datetime.datetime.now()}\n')
                                salidaMenu = 0
                                
                                
                            else:
                                print(comprador['name'], " No tiene los suficientes puntos")
                                accion = int(input("1) pagar Efectivo\n2) cancelar compra\n"))
                                if accion == 2:
                                    accion = -1
                                elif accion == 1:
                                    metodoPago = 1
                            
                        if metodoPago == 1:
                            pago = float(input('Con cuanto paga: '))
                            while (pago < total):

                                print('valor menor al total')
                                pago = float(input('Con cuanto paga: '))

                            cambio = pago - total

                            if (cambio > 0):
                                print('El cambio es de: ', cambio)
                                
                            newVenta = {}
                            newVenta['carrito'] = {}

                            for i in carrito:
                                inventario.update_one({'_id': i}, {'$set': {'cantidad': inventario.find_one({'_id': i})['cantidad'] - carrito[i]['cantidad']}})
                                newVenta['carrito'][i] = {'cantidad': carrito[i]['cantidad'], 'precio': carrito[i]['unidad']}

                            newVenta['total'] = total
                            newVenta['cambio'] = cambio

                            if (fecha_entrada == ""):
                                newVenta['fecha'] = datetime.datetime.now().strftime("%d-%m-%Y")

                            else:
                                newVenta['fecha'] = fecha_entrada

                            newVenta['comprador'] = 'Anonimo' if idComprador == "" else {'id': idComprador, 'name': usuarios.find_one({'_id': idComprador})['name']}
                            newVenta['vendedor'] = {'id': userID['_id'], 'name': userID['name']}
                            carrito = {}
                                
                            if (idComprador != ""):

                                puntos = total // 1000
                                comprador = usuarios.find_one({'_id': idComprador})
                                usuarios.update_one({'_id': idComprador}, {'$set': {'APUntos': comprador['APUntos'] + puntos}})
                                print(comprador["name"], " ha sumado ", puntos, " APUntos")
                                
                            ventas.insert_one(newVenta)
                            print('!!Compra realizada exitosamente!!')
                            log(f'{userID["_id"]} realizo una venta a {newVenta["comprador"]} con efectivo por un total de {total}$ el {datetime.datetime.now()}\n')
                            salidaMenu2 = int(input('Presiona 0 para salir o cualquier otro numero para seguir registrando ventas\n'))
                            salidaMenu = 0

                if (accion == 0):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    salidaMenu = 0
                
                elif (accion == -1):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    salidaMenu = 0
                    salidaMenu2 = 0
                    
            else:
                print('El inventario esta vacio')
                salidaMenu = 0

        

# Función para visualizar los usuarios registrados
def verUsuarios():
    global usuarios
    accion = None
    # Carga y muestra de usuarios desde el archivo JSON en consola
    while (accion != 0):
        time.sleep(tiempo)
        os.system('cls' if os.name == 'nt' else 'clear')
        time.sleep(tiempo)
        os.system('cls' if os.name == 'nt' else 'clear')

        if (usuarios.count_documents({}) > 0):

            print('| {:<15} | {:<25} | {:<15} | {:<10} |'.format('Id', 'Nombre', 'Rol', 'APUntos'))
            print('-' * (15 + 25 + 15 + 10 + 13))

            for usuario in usuarios.find():
                print('| {:<15} | {:<25} | {:<15} | {:<10} |'.format(usuario['_id'], usuario['name'], usuario['rol'], usuario['APUntos']))
        else:
            print('No hay usuarios registrados')

        log(f'{userID["_id"]} vió los usuarios el {datetime.datetime.now()}\n')
        accion = int(input('Presiona 0 para salir\n'))

# Función para actualizar el inventario
def actualizarInventario():
    # Carga del inventario y permitir al usuario agregar, actualizar o eliminar productos
    # Guardado de cambios en el archivo JSON correspondiente
    global inventario
    salidaMenu = None
    while (salidaMenu != "0"):

        time.sleep(tiempo)
        os.system('cls' if os.name == 'nt' else 'clear')

        print(' 1. Agregar producto\n 2. Actualizar producto\n 3. Eliminar producto\n 0. Salir')
        accion = int(input('Que deseas hacer: '))

        if (accion == 1):

            time.sleep(tiempo)
            os.system('cls' if os.name == 'nt' else 'clear')
            newItemName = input('Cual es el nombre del nuevo producto: ')
            newItemNum = int(input('Cantidad : '))
            newPrice = int(input('Precio unitario: '))
            inventario.insert_one({'_id': newItemName, 'cantidad': newItemNum, 'precio' : newPrice})
            log(f'{userID["_id"]} agrego {newItemNum} del nuevo producto {newItemName} con precio: {newPrice} el {datetime.datetime.now()}')
            print('!!Producto agregado exitosamente!!')
            
        elif (accion == 2):

            if (inventario.count_documents({}) == 0):
                print("El inventario esta vacio")
                salidaMenu = "0"

            else:
                time.sleep(tiempo)
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Presiona 0 para salir")   
                item = input('Que producto quieres actualizar: ')

                if (item != "0"):
                    while (inventario.find_one({'_id': item}) == None):
                        time.sleep(tiempo)
                        os.system('cls' if os.name == 'nt' else 'clear')
                        print('No existe el producto ', item)
                        item = input('Que producto quieres actualizar: ')
                    print(' 1. Nombre\n 2. Cantidad\n 3. Precio\n 4. Todos\n 0. Salir')
                    actualizarMenu = int(input('Que se va a actualizar: '))
                    oldItem = inventario.find_one({'_id': item})

                    if (actualizarMenu == 1):
                        print('Nombre actual: ', item)
                        updateName = input("Nuevo nombre: ")
                        inventario.delete_one({'_id': item})
                        oldItem['_id'] = updateName
                        inventario.insert_one(oldItem)
                        
                        log(f'{userID["_id"]} cambio el nombre de {item} a {updateName} el {datetime.datetime.now()}\n')

                    elif (actualizarMenu == 2):
                        print('Cantidad actual: ', oldItem['cantidad'])
                        updateCantidad = int(input("Nueva cantidad: "))
                        inventario.update_one({'_id': item}, {'$set': {'cantidad': updateCantidad}})
                        log(f'{userID["_id"]} cambio la cantidad de {item} de {oldItem["cantidad"]} a {updateCantidad} el {datetime.datetime.now()}\n')

                    elif (actualizarMenu == 3):
                        print('Precio actual: ', oldItem['precio'])
                        updatePrice = input("Nuevo precio: ")
                        inventario.update_one({'_id': item}, {'$set': {'precio': updatePrice}})
                        log(f'{userID["_id"]} cambio el precio de {item} de {oldItem["precio"]} a {updatePrice} el {datetime.datetime.now()}\n')

                    elif (actualizarMenu == 4):
                        print('Nombre actual: ', item)
                        updateName = input("Nuevo nombre: ")
                        print('Cantidad actual: ', oldItem['cantidad'])
                        newItemNum = int(input('Cantidad : '))
                        print('Precio actual: ', oldItem['precio'])
                        newPrice = int(input('Precio unitario: '))
                        inventario.delete_one({'_id': item})
                        inventario.insert_one({'_id': updateName, 'cantidad': newItemNum, 'precio' : newPrice})
                        log(f'{userID["_id"]} cambio el nombre de {item} a {updateName} la cantidad de {oldItem["cantidad"]} a {newItemNum} y el precio de {oldItem["precio"]} a {newPrice} el {datetime.datetime.now()}\n')
                    else:
                        salidaMenu = "0"

                    if (actualizarMenu != 0):
                        print('!!Producto actualizado exitosamente!!')

                else:
                    salidaMenu = "0"

        elif (accion == 3):
            time.sleep(tiempo)
            os.system('cls' if os.name == 'nt' else 'clear')
            item = input('Que producto quieres eliminar (presiona 0 para salir): ')
            delItem = inventario.find_one({'_id': item})

            while (delItem == None and item != "0"):
                time.sleep(tiempo)
                os.system('cls' if os.name == 'nt' else 'clear')
                print('No existe el producto ', item)
                item = input('Que producto quieres eliminar: ')
                delItem = inventario.find_one({'_id': item})

            if (delItem != None and item != "0"):
                inventario.delete_one({'_id': item})
                log(f'{userID["_id"]} elimino el producto {item} el {datetime.datetime.now()}\n')
                print('!!Producto eliminado exitosamente!!')

        elif (accion == 0):
            salidaMenu = 0

        if (salidaMenu != "0"):
            print('Presiona 0 para salir')
            salidaMenu = input()  
        
# Función para ver el inventario
def verInventario():
    # Carga y muestra del inventario desde el archivo JSON
    global inventario
    accion = None
    filtro = None
    
    time.sleep(tiempo)
    os.system('cls' if os.name == 'nt' else 'clear')
    print("1) ver todo el inventario\n2) ver productos con pocas unidades\n0) Salir")
    filtro = int(input("Que quieres hacer: "))
    while (filtro != 1 and filtro != 2 and filtro != 0):
        print("opcion invalida")
        filtro = int(input("Que quieres hacer: "))
    
    if (filtro == 1):
        while (accion != 0):

            time.sleep(tiempo)
            os.system('cls' if os.name == 'nt' else 'clear')
            time.sleep(tiempo)
            os.system('cls' if os.name == 'nt' else 'clear')

            if (inventario.count_documents({}) > 0):

                print('| {:<20} | {:<10} | {:<10} |'.format('Producto', 'Cantidad', 'Precio'))
                print('-' * (20 + 10 + 10 + 10))

                for producto in inventario.find():
                    print('| {:<20} | {:<10} | {:<10} |'.format(producto['_id'], producto['cantidad'], producto['precio']))

            else:
                print('El inventario esta vacio')
            
            
            accion = int(input('Presiona 0 para salir\n'))
    elif (filtro == 2):
        while (accion != 0):

            time.sleep(tiempo)
            os.system('cls' if os.name == 'nt' else 'clear')
            time.sleep(tiempo)
            os.system('cls' if os.name == 'nt' else 'clear')

            if (inventario.count_documents({}) > 0):
                cont = 0
                print('| {:<20} | {:<10} | {:<10} |'.format('Producto', 'Cantidad', 'Precio'))
                print('-' * (20 + 10 + 10 + 10))

                for producto in inventario.find():
                    if producto['cantidad'] <= 2:
                        cont += 1
                        print('| {:<20} | {:<10} | {:<10} |'.format(producto['_id'], producto['cantidad'], producto['precio']))
                if cont == 0:
                    print("!!No hay productos con pocas unidades!!")

            else:
                print('El inventario esta vacio')
            
            
            accion = int(input('Presiona 0 para salir\n'))
    else:
        accion = 0
    
    log(f'{userID["_id"]} vió el inventario el {datetime.datetime.now()}\n')

# Función para crear un nuevo usuario
def crearUsuario():
    # Proceso para agregar un nuevo usuario, incluyendo validaciones de datos
    # Guardado de datos actualizados en archivo JSON
    global usuarios
    salidaMenu = None
    while (salidaMenu != "0"):
        while (salidaMenu != "0"):
            time.sleep(tiempo)
            os.system('cls' if os.name == 'nt' else 'clear')
            print('Crear usuario:')
            newIdUser = input('Nuevo Id de usuario: ')
            newUserName = input('Nuevo nombre de usuario: ')
            newUserPassword = input('Nueva password: ')
            newRol = input('Nuevo Rol: ')

            while (newRol not in roles or usuarios.find_one({'_id': newIdUser}) != None):
                time.sleep(tiempo)
                os.system('cls' if os.name == 'nt' else 'clear')
                print('**!!Datos Invalidos!!**')
                print('Crear Usuario:')
                newIdUser = input('Nuevo Id de usuario: ')
                newUserName = input('Nuevo nombre de usuario: ')
                newUserPassword = input('Nuevo password: ')
                newRol = input('Nuevo Rol: ')

            usuarios.insert_one({'_id': newIdUser,'name': newUserName, 'password' : newUserPassword, 'rol' : newRol, 'APUntos': 0, 'logged': False})

            print('Usuario ', newRol, ' creado exitosamente!!! :)')
            log(f'{userID["_id"]} creo el usuario con id: {newIdUser}, con rol: {newRol} y contraseña: {newUserPassword} el {datetime.datetime.now()}\n')

            salidaMenu = input('Presione Enter para seguircreando usuarios o escriba 0 y pulse Enter para salir\n')
    
# Función para iniciar sesión
def login():
    global usuarios, userID
    # Proceso de inicio de sesión, con validación de credenciales
    # Carga de usuarios desde el archivo JSON si existe, o creación de un usuario administrador predeterminado

    os.system('cls' if os.name == 'nt' else 'clear')

    userID = None
    password = None
    SalidaLogin = True

    while (SalidaLogin):
        userID = input('Id: ')
        password = input('Contraseña: ')
        User = usuarios.find_one({'_id': userID, 'password': password})
        if (User != None):
            if (not User['logged']): 
                SalidaLogin = False
                usuarios.update_one(User, {'$set': {'logged': True}})
            else:
                print("El usuario con id:", userID, "ya esta logeado")
                
        else:
            print('Usuario o contraseña no validos')
            time.sleep(tiempo)
            os.system('cls' if os.name == 'nt' else 'clear')

    userID = User
    print(f'¡Bienvenido {User["name"]}!')
    log(f'{User["_id"]} inicio sesion el {datetime.datetime.now()}\n')
    
def log(txt):
    with open(FileLog, "a") as archivo:
        archivo.write(txt)

def comprasDiarias():
    global usuarios, userID

    os.system('cls' if os.name == 'nt' else 'clear')
    total = 0

    if (ventas.count_documents({}) == 0):
        print('No hay ventas registradas')
        time.sleep(tiempo)
        os.system('cls' if os.name == 'nt' else 'clear')
        return
    
    print('Ingrese la fecha de las compras en el formato DD-MM-YYYY (presione enter si es de hoy)\n Presione 0 para salir')
    fecha = input()

    if (fecha == "0"):
        time.sleep(tiempo)
        os.system('cls' if os.name == 'nt' else 'clear')
        return

    if (fecha == ""):
        fecha = datetime.datetime.now().strftime("%d-%m-%Y")

    print('Ventas del dia ', fecha)

    if (ventas.count_documents({'fecha': fecha}) == 0):
        print('No hay ventas registradas para esta fecha')
        time.sleep(tiempo)
        os.system('cls' if os.name == 'nt' else 'clear')
        return

    for venta in ventas.find({'fecha': fecha}):
            print('Vendedor: ', venta['vendedor']['name'], '- Id: ', venta['vendedor']['id'])
            print('Comprador: ', venta['comprador']['name'],'- Id: ',venta['comprador']['id']) if venta['comprador'] != 'Anonimo' else print('Comprador: Anonimo')
            print('Total de la venta: ', venta['total'], 'Cambio: ', venta['cambio'])
            
            print('\n| {:<20} | {:<10} | | {:<10} |'.format('Producto', 'Cantidad', 'Precio'))
            print('-' * (20 + 10 + 10 + 12))

            for j in venta['carrito']:
                print('| {:<20} | {:<10} | | {:<10} |'.format(j, venta['carrito'][j]['cantidad'], venta['carrito'][j]['precio']))
                
            print('-' * (20 + 10 + 10 + 12), )
            total += venta['total']

    print('Total del día: ', total)
    print('Presiona 0 para salir')
    log(f'{userID["_id"]} vió las el reporte de ventas el {datetime.datetime.now()}\n')
    accion = input()
    time.sleep(tiempo)
    os.system('cls' if os.name == 'nt' else 'clear')

# Menú principal del sistema, muestra opciones según el rol del usuario logueado
def menu():
    # Presentación de opciones y navegación por el sistema basado en el rol del usuario
    # Llamadas a las funciones correspondientes según la selección del usuario
    print('    ___    ____  __  __')
    print('   /   |  / __ \/ / / /')
    print('  / /| | / /_/ / / / / ')
    print(' / ___ |/ ____/ /_/ /  ')
    print('/_/  |_/_/    \____/   \n')
    print(f'Usuario: {userID["name"]} - Id: {userID["_id"]}')
    if (userID['rol'] == 'administrador'):
        print(' 1. Crear usuario\n 2. Actualizar inventario\n 3. Ver inventario\n 4. Ver usuarios\n 5. Registrar venta\n 6. Compras diarias\n 0. Salir')
        print('\n© 2024 PaticOS S.A. All rights reserved \n')
        accion = int(input('Que deseas hacer: '))

        if (accion == 1):
            crearUsuario()

        elif (accion == 2):
            actualizarInventario()

        elif (accion == 3):
            verInventario()

        elif (accion == 4):
            verUsuarios()

        elif (accion == 5):
            realizarVenta()

        elif (accion == 6):
            comprasDiarias()

        else:
            usuarios.update_one(userID, {'$set': {'logged': False}})
            log(f'{userID["_id"]} vió las el reporte de ventas el {datetime.datetime.now()}\n')
            return 0
        
    elif (userID['rol'] == 'cliente'):
        print(' 1. Ver inventario\n 2. Ver mis APUntos\n 0. Salir')
        print('\n© 2024 PaticOS S.A. All rights reserved \n')
        accion = int(input('Que deseas hacer: '))

        if (accion == 1):
            verInventario()
            
        elif(accion == 2):
            verAPUntos()

        else:
            usuarios.update_one(userID, {'$set': {'logged': False}})
            log(f'{userID["_id"]} vió las el reporte de ventas el {datetime.datetime.now()}\n')
            return 0
        
    elif (userID['rol'] == 'trabajador'):
        print(' 1. Actualizar inventario\n 2. Ver inventario\n 3. Registrar venta\n 0. Salir')
        print('\n© 2024 PaticOS S.A. All rights reserved \n')
        accion = int(input('Que deseas hacer: '))

        if (accion == 1):
            actualizarInventario()

        elif (accion == 2):
            verInventario()

        elif (accion == 3):
            realizarVenta()

        else:
            usuarios.update_one(userID, {'$set': {'logged': False}})
            log(f'{userID["_id"]} vió las el reporte de ventas el {datetime.datetime.now()}\n')
            return 0

# Bucle principal del programa, maneja el login y la navegación por el menú principal
while (True):
    login()
    salidaMenu = None

    while (salidaMenu != 0):
        time.sleep(tiempo)
        os.system('cls' if os.name == 'nt' else 'clear')
        salidaMenu = menu()
    if (userID != None):
        usuarios.update_one({'_id': userID['_id']}, {'$set': {'logged': False}})

'''
    ___    ____  __  __
   /   |  / __ \/ / / /
  / /| | / /_/ / / / / 
 / ___ |/ ____/ /_/ /  
/_/  |_/_/    \____/   

'''