import json
import os
import time
import datetime
from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://Finchi:Juanjose.123@cluster0.pndlt5o.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
FileLog = "log.txt"
roles = {'cliente', 'trabajador', 'administrador', 'proveedor'}
tiempo = 1
userID = None

# Nombres de la base de datos y colecciones a utilizar

client = MongoClient(uri) 

db = client['Procesos']

inventario = db['inventario']
ventas = db['ventas']
usuarios = db['usuarios']
proveedores = db['proveedores']


# Función para ver los APUntos de un cliente
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

    # Proceso para realizar una venta, incluyendo la selección de productos y el método de pago
    # Guardado de la venta en la colección correspondiente

    salidaMenu2 = None

    while (salidaMenu2 != 0):

        carrito = {}

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
                    
                    inventario.update_one({'_id': item}, {'$set': {'cantidad': item2['cantidad'] - cantidad}})

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
                        metodoPago = 1
                        if (idComprador != ""):
                            print(" 1. Efectivo\n 2. APUntos")
                            metodoPago = int(input("Metodo de pago: "))

                        if (metodoPago == 2):
                            comprador = usuarios.find_one({'_id': idComprador})

                            if comprador['APUntos'] * 4 >= total:
                                usuarios.update_one({'_id': idComprador}, {'$set': {'APUntos': comprador['APUntos'] - (total // 4)}})
                                
                                cambio = 'APUntos'
                                
                                log(f'{userID["_id"]} realizo una venta a {idComprador} con APUntos por un total de {total}$ el {datetime.datetime.now()}\n')
                                salidaMenu = 0
                                
                            else:
                                print(comprador['name'], " No tiene los suficientes puntos")
                                accion = int(input("1) pagar Efectivo\n2) cancelar compra\n"))

                                if (accion == 2):
                                    accion = -1

                                elif (accion == 1):
                                    metodoPago = 1
                            
                        if metodoPago == 1:
                            pago = float(input('Con cuanto paga: '))
                            while (pago < total):

                                print('Valor menor al total')
                                pago = float(input('Con cuanto paga: '))

                            cambio = pago - total

                            if (cambio > 0):
                                print('El cambio es de: ', cambio)

                            if (idComprador != ""):

                                puntos = total // 1000
                                comprador = usuarios.find_one({'_id': idComprador})
                                usuarios.update_one({'_id': idComprador}, {'$set': {'APUntos': comprador['APUntos'] + puntos}})
                                print(comprador["name"], " ha sumado ", puntos, " APUntos")
                                log(f'{userID["_id"]} realizo una venta a {idComprador} con efectivo por un total de {total}$ el {datetime.datetime.now()}\n')

                            else:
                                log(f'{userID["_id"]} realizo una venta a Anonimo con efectivo por un total de {total}$ el {datetime.datetime.now()}\n')
                                
                        newVenta = {}

                        if (fecha_entrada == ""):
                            newVenta['fecha'] = datetime.datetime.now().strftime("%d-%m-%Y")

                        else:
                            newVenta['fecha'] = fecha_entrada
                        
                        newVenta['carrito'] = {}

                        for i in carrito:
                            newVenta['carrito'][i] = {'cantidad': carrito[i]['cantidad'], 'precio': carrito[i]['unidad']}
                            
                        newVenta['total'] = total
                        newVenta['cambio'] = cambio

                        newVenta['vendedor'] = {'id': userID['_id'], 'name': userID['name']}
                        newVenta['comprador'] = 'Anonimo' if idComprador == "" else {'id': idComprador, 'name': usuarios.find_one({'_id': idComprador})['name']}
                                
                        ventas.insert_one(newVenta)
                        print('!!Compra realizada exitosamente!!')
                        salidaMenu2 = int(input('Presiona 0 para salir o cualquier otro numero para seguir registrando ventas\n'))
                        salidaMenu = 0

                if (accion == 0):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    salidaMenu = 0

                    for i in carrito:
                        item = inventario.find_one({'_id': i})
                        inventario.update_one({'_id': i}, {'$set': {'cantidad': item['cantidad'] + carrito[i]['cantidad']}})
                
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
    global inventario
    # Proceso para actualizar el inventario, incluyendo la selección de productos y la modificación de sus atributos
    # Guardado de los cambios en la colección correspondiente
    salidaMenu = None
    while (salidaMenu != "0"):

        time.sleep(tiempo)
        os.system('cls' if os.name == 'nt' else 'clear')

        print(' 1. Agregar producto\n 2. Actualizar producto\n 3. Eliminar producto\n 0. Salir')
        accion = int(input('Que deseas hacer: '))

        if (accion == 1):
            global proveedores
            newProveedores = {}
            time.sleep(tiempo)
            os.system('cls' if os.name == 'nt' else 'clear')
            newItemName = input('Cual es el nombre del nuevo producto: ')
            newItemNum = int(input('Cantidad : '))
            newPrice = int(input('Precio unitario: '))
            newProveedor = input('Agrega el nombre del proveedor: ')
            while (newProveedor != ""):
                busqueda = proveedores.find_one({'name': newProveedor})
                if (busqueda != None):
                    busqueda = busqueda['items']
                    busqueda[newItemName] = None 
                    proveedores.update_one({'name': newProveedor}, {'$set': {'items': busqueda}})
                    newProveedores[newProveedor] = None
                else:
                    if (busqueda == None):
                        print("Este proveedor no se encuentra dentro de la base de datos")
                    else:
                        print("si mas proveedores no distribuyen este producto pulsa Enter")
                newProveedor = input('Agrega el nombre del proveedor: ')
                
                
            inventario.insert_one({'_id': newItemName, 'cantidad': newItemNum, 'precio' : newPrice, 'proveedores': newProveedores})
            log(f'{userID["_id"]} agrego {newItemNum} del nuevo producto {newItemName} con precio: {newPrice} y los proveedores: {newProveedores} el {datetime.datetime.now()}\n')
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
                    print(' 1. Nombre\n 2. Cantidad\n 3. Precio\n 4. Proveedor\n 0. Salir')
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
                        listaProveedores = list(oldItem['proveedores'].keys())
                        print('Proveedores actuales: ', *listaProveedores)
                        print(' 1. Agregar proveedor\n 2. Eliminar proveedor\n 0. Salir')
                        accionProveedor = int(input('Que deseas hacer: '))

                        if(accionProveedor == 1):
                            proveedor = input('Nombre del proveedor: ')
                            busqueda = proveedores.find_one({'name': proveedor})
                            if (busqueda != None):
                                busqueda = busqueda['items']
                                busqueda[item] = None 
                                proveedores.update_one({'name': proveedor}, {'$set': {'items': busqueda}})
                                oldItem['proveedores'][proveedor] = None
                                inventario.update_one({'_id': item}, {'$set': {'proveedores': oldItem['proveedores']}})
                                log(f'{userID["_id"]} agrego el proveedor {proveedor} al producto {item} el {datetime.datetime.now()}\n')
                            else:
                                if (busqueda == None):
                                    print("Este proveedor no se encuentra dentro de la base de datos")
                                else:
                                    print("si mas proveedores no distribuyen este producto pulsa Enter")
                        elif(accionProveedor == 2):
                            proveedor = input('Nombre del proveedor: ')
                            busqueda = proveedores.find_one({'name': proveedor})
                            if (busqueda != None):
                                proveedores.update_one({'name': proveedor}, {'$unset': {f'items.{item}': ''}})
                                inventario.update_one({'_id': item}, {'$unset': {f'proveedores.{proveedor}': ''}})
                                log(f'{userID["_id"]} elimino el proveedor {proveedor} del producto {item} el {datetime.datetime.now()}\n')
                            else:
                                if (busqueda == None):
                                    print("Este proveedor no se encuentra dentro de la base de datos")
                                else:
                                    print("si mas proveedores no distribuyen este producto pulsa Enter")

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
                for proveedor in delItem['proveedores']:
                    proveedores.update_one({'name': proveedor}, {'$unset': {f'items.{item}': ''}})
                log(f'{userID["_id"]} elimino el producto {item} el {datetime.datetime.now()}\n')
                print('!!Producto eliminado exitosamente!!')

        elif (accion == 0):
            salidaMenu = 0

        if (salidaMenu != "0"):
            print('Presiona 0 para salir')
            salidaMenu = input()  
        
# Función para ver el inventario
def verInventario(): 
    # Proceso para visualizar el inventario, según el rol del usuario logueado
    # Muestra los productos del proveedor o todos los productos
    # Muestra los productos con pocas unidades
    global inventario
    global userID
    accion = None
    filtro = None
    
    time.sleep(tiempo)
    os.system('cls' if os.name == 'nt' else 'clear')
    if (userID['rol'] == 'proveedor'):
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
                    if ( userID['name'] in producto['proveedores']):
                        cont += 1
                        print('| {:<20} | {:<10} | {:<10} |'.format(producto['_id'], producto['cantidad'], producto['precio']))
                if cont == 0:
                    print("!!No hay productos con pocas unidades!!")

            else:
                print('El inventario esta vacio')
            
            
            accion = int(input('Presiona 0 para salir\n'))
    else:
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

                    for producto in inventario.find({'cantidad': {'$lte': 5}}):
                        print('| {:<20} | {:<10} | {:<10} |'.format(producto['_id'], producto['cantidad'], producto['precio']))
                        cont += 1
                    if (cont == 0):
                        print("!!No hay productos con pocas unidades!!")

                else:
                    print('El inventario esta vacio')
                
                
                accion = int(input('Presiona 0 para salir\n'))
        else:
            accion = 0
    
    log(f'{userID["_id"]} vió el inventario el {datetime.datetime.now()}\n')

# Función para crear un nuevo usuario
def crearUsuario():
    # Proceso para crear un nuevo usuario
    # Validación de datos y guardado del usuario en la colección correspondiente

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
            newContact = input("Numero de contacto:")
            newRol = input('Nuevo Rol: ')

            while (newRol not in roles or usuarios.find_one({'_id': newIdUser}) != None):
                time.sleep(tiempo)
                os.system('cls' if os.name == 'nt' else 'clear')
                print('**!!Datos Invalidos!!**')
                print('Crear Usuario:')
                newIdUser = input('Nuevo Id de usuario: ')
                newUserName = input('Nuevo nombre de usuario: ')
                newUserPassword = input('Nuevo password: ')
                newContact = input("Numero de contacto:")
                newRol = input('Nuevo Rol: ')

            usuarios.insert_one({'_id': newIdUser,'name': newUserName, 'password' : newUserPassword, 'rol' : newRol, 'APUntos': 0, 'logged': False, 'contact': newContact})

            print('Usuario ', newRol, ' creado exitosamente!!! :)')
            log(f'{userID["_id"]} creo el usuario con id: {newIdUser}, con rol: {newRol} y contraseña: {newUserPassword} el {datetime.datetime.now()}\n')
            if( newRol == "proveedor" ):
                global proveedores
                proveedores.insert_one({'_id': newIdUser,'name': newUserName, 'contact': newContact, 'items': {}})
                
            salidaMenu = input('Presione Enter para seguir creando usuarios o escriba 0 y pulse Enter para salir\n')
    
# Función para iniciar sesión
def login():
    global usuarios, userID
    # Proceso para iniciar sesión, incluyendo la validación de credenciales y el cambio de estado del usuario a logueado

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

# Función para registrar las acciones de los usuarios 
def log(txt):
    with open(FileLog, "a") as archivo:
        archivo.write(txt)

# Función para visualizar las compras diarias
def comprasDiarias():
    global usuarios, userID
    # Proceso para visualizar las compras diarias, incluyendo la selección de la fecha

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
    log(f'{userID["_id"]} vio las el reporte de ventas el {datetime.datetime.now()}\n')
    accion = input()
    time.sleep(tiempo)
    os.system('cls' if os.name == 'nt' else 'clear')

# Menú principal del sistema, muestra opciones según el rol del usuario logueado
def menu():
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
            log(f'{userID["_id"]} cerro sesion el {datetime.datetime.now()}\n')
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
            log(f'{userID["_id"]} cerro sesion el {datetime.datetime.now()}\n')
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
            log(f'{userID["_id"]} cerro sesion el {datetime.datetime.now()}\n')
            return 0
    elif (userID['rol'] == 'proveedor'):
        print(' 1. Ver inventario\n 2. Ver mis APUntos\n 0. Salir')
        print('\n© 2024 PaticOS S.A. All rights reserved \n')
        accion = int(input('Que deseas hacer: '))

        if (accion == 1):
            verInventario()
            
        elif(accion == 2):
            verAPUntos()

        else:
            usuarios.update_one(userID, {'$set': {'logged': False}})
            log(f'{userID["_id"]} cerro sesion el {datetime.datetime.now()}\n')
            return 0

# Bucle principal del programa, maneja el login y hace llamado al menú
try:
    while (True):
        login()
        salidaMenu = None
        try:
            while (salidaMenu != 0):
                time.sleep(tiempo)
                os.system('cls' if os.name == 'nt' else 'clear')
                salidaMenu = menu()
            if (userID != None):
                usuarios.update_one({'_id': userID['_id']}, {'$set': {'logged': False}})
        except:
            usuarios.update_one({'_id': userID['_id']}, {'$set': {'logged': False}})
            break
except KeyboardInterrupt:
    if (userID != None):
        usuarios.update_one({'_id': userID['_id']}, {'$set': {'logged': False}})

'''
    ___    ____  __  __
   /   |  / __ \/ / / /
  / /| | / /_/ / / / / 
 / ___ |/ ____/ /_/ /  
/_/  |_/_/    \____/   

'''