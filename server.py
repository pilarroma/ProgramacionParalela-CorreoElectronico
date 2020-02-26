from multiprocessing.connection import Listener,Client
from multiprocessing import Process,Manager

def newuser(conn,messages,contacts,keys,password,status,user,m): 
    validuser = (len(user)>=1 and user[0] <> '')	
    if user in contacts or not validuser:
        conn.send(["notify_new",(False,"ERROR.Nuevo usuario introducido no esta permitido")])	
    else:
	keys[user] = password	
	contacts[user] = m[2]
	messages[user] = []   
        status[user] = False
	conn.send(["notify_new",(True,"Registro correcto")])	

def seguridad(user,keys,password):
    return ((user in keys) and (keys[user] == password))

def notificarconexion(conexiones,user,contacts,status,con):
    for usuario in status.keys():
        if status[usuario] and user in contacts[usuario]:
            conlocal= Client(address=conexiones[usuario][0],authkey = conexiones[usuario][1])
            if con:
                conlocal.send(["server_notify_connected_user",user])
	    else:
                conlocal.send(["server_notify_quit_user",user])
 	    conlocal.close()
	
def connect(conn,messages,contacts,keys,password,user,conexlocales,m,status):
    if seguridad(user,keys,password) and status[user] == False:
        print "1"
        status[user] = True
        conexlocales[user] = m[2]
        conn.send(["notify_connect", (True,"Conexion correcta")])
        notificarconexion(conexlocales,user,contacts,status,True)
    elif user not in contacts:
   	print "2"
	conn.send(["notify_connect", (False,"ERROR.Conexion no permitida.No eres un usuario")])
    elif password <> keys[user]:
        print "3"
	conn.send(["notify_connect", (False,"ERROR.Conexion no permitida.Password incorrecta")])
    else:
        print "4"
        conn.send(["notify_connect", (False,"ERROR.Ya estas conectado")]) 	

def get_messages(conn,messages,contacts,keys,status,password,user):
    if seguridad(user,keys,password) and status[user]:
        conn.send(["notify_get_messages",(True,messages[user])])
	messages[user] = []
    else:
	conn.send(["notify_get_messages",(False,[])])

def send(conn,messages,contacts,keys,status,password,user,m):  
    if seguridad(user,keys,password) and status[user]:
        print 'm',m
        print 'm[2]',m[2]
        destinatario = m[2][0]
        if destinatario in messages:
            if destinatario in contacts[user]: 
                messages[destinatario]+=[(user,m[2][1])]
                envio =(True, "Mensaje enviado correctamente")
            else:
                envio = (False, "ERROR.Nombre introducido no esta en tus contactos")	  
        else:
            envio = (False, "ERROR.Nombre introducido no esta registrado")
    else:
        envio = (False,"ERROR.Usuario o password incorrecto")
    conn.send(["notify_send",envio])

def new_adbook_contact(conn,contacts,keys,status,password,user,m):
    lista = []
    if seguridad(user,keys,password) and status[user]:
        if len(m[2])>0:
            for usuario in m[2]:
                if usuario not in contacts[user]:
                    contacts[user] = contacts[user]+[usuario]
                    explicacion = " agregado correctamente" 
                    add = True
                else:
                    add = False
                    explicacion = " ya en tu listin" 
                envio = (add,explicacion)
                lista.append(envio)
        else:
          lista = [(False,"ERROR.Debes introducir un contacto para agregar a tu listin")]   
    elif not seguridad(user,keys,password):
        lista = [(False,"ERROR.Usuario o password incorrecta")]
        if len(m[2])>1:
            lista = lista*len(m[2])
    else:
        lista = [(False,"ERROR.Usuario no conectado")]
        if len(m[2])>1:
            lista = lista*len(m[2])
    conn.send(["notify_new_addressbook_contact",lista])

def del_adbook_contact(conn,contacts,keys,status,password,user,m):
    lista = []
    if seguridad(user,keys,password) and status[user]:
        if len(m[2])>0:
            for usuario in m[2]: 	
                if usuario in contacts[user]:
                    con = contacts[user]
                    con.remove(usuario)
                    contacts[user] = con
                    explicacion = " eliminado correctamente"
                    delat = True
                else:
                    delat = False
                    explicacion = "ERROR.Contacto no esta en tu listin"
                envio = (delat,explicacion)
                lista.append(envio)
        else:
            lista = [(False,"ERROR.Debes seleccionar un contacto para poder eliminarlo.")]
    elif not seguridad(user,keys,password):
       lista = [(False,"ERROR.Usuario o password incorrecta")]
       if len(m[2])>1:
          lista = lista*len(m[2])
    else:
       lista = [(False,"ERROR.Usuario no conectado")] 
       if len(m[2])>1:
          lista = lista*len(m[2])           
    conn.send(["notify_del_addresbook_contact",lista]) 	

def fquit(conn,keys,user,password,conexlocales,status,contacts): 
    if seguridad(user,keys,password) and status[user]:
        conn.send(["notify_quit",(True,"Conexion cerrada")])
        print "conexion cerrada"
        status[user] = False
	conn.close()
	notificarconexion(conexlocales,user,contacts,status,False)
        return True	
    elif not seguridad(user,keys,password):
	conn.send(["notify_quit",(False,"ERROR.Usuario o password incorrecta")])
        return False
    else:
        conn.send(["notify",(False,"ERROR.No estas conectado")])	
        return False 	 

def get_status(conn,user,password,status,keys,contacts):
    if seguridad(user,keys,password) and status[user]:	
        estadoscontactos = {}
        for contacto in contacts[user]:
            if contacto in status:
                estadoscontactos[contacto] = status[contacto]
            else:
                estadoscontactos[contacto] = False
        conn.send(["notify_get_addressbook_status",(True,estadoscontactos)])
    else:
        conn.send(["notify_get_addressbook_status",(False,{})])

def chat(conn,user,password,conexiones,keys,status,m,contacts):
    if seguridad(user,keys,password) and status[user]:
        print 'm',m
        print 'm[2]',m[2]
        destinatario = m[2][0]
        if destinatario in status and status[destinatario]:
            if destinatario in contacts[user]: 
                conlocal= Client(address=conexiones[destinatario][0],authkey = conexiones[destinatario][1])
                conlocal.send(["server_notify_chat",(user,m[2][1])])
                conlocal.close()
                envio =(True, "Mensaje enviado correctamente")
            else:
                envio = (False, "ERROR.Nombre introducido no esta en tus contactos")	  
        else:
            envio = (False, "ERROR.Nombre introducido no esta conectado")
    else:
        envio = (False,"ERROR.Usuario o password incorrecto")
    conn.send(["notify_chat",envio])
       
def serve_client(conn,id,messages,contacts,keys,conexlocales,status):
    while True:
        try:
	    m = conn.recv()
	    user = m[0][0]
	    password = m[0][1]	
	except EOFError:
	    print "connection abruptly closed by client"
	    break
        print "received message:", m
	if m[1] == "new_user":
	    newuser(conn,messages,contacts,keys,password,status,user,m)
	elif m[1] == "connect":
	    connect(conn,messages,contacts,keys,password,user,conexlocales,m,status)  
	elif m[1] == "get_messages":
	    get_messages(conn,messages,contacts,keys,status,password,user)
        elif m[1] == "send":
	    send(conn,messages,contacts,keys,status,password,user,m) 
	elif m[1] == "new_addressbook_contact":
	    new_adbook_contact(conn,contacts,keys,status,password,user,m)
	elif m[1] == "del_addressbook_contact": 
	    del_adbook_contact(conn,contacts,keys,status,password,user,m)  
        elif m[1] == "get_addressbook_status":
            get_status(conn,user,password,status,keys,contacts) 
        elif m[1] == "chat":
            chat(conn,user,password,conexlocales,keys,status,m,contacts)
	elif m[1] == "quit": 
	    if fquit(conn,keys,user,password,conexlocales,status,contacts): 
                conn.close()
                break   
    print id,"connection close"
	       
if __name__ == "__main__":
    
    ipsalaorden = "147.96.18.64"
    ipclase = "147.96.18.188"
    ipcasa = "127.0.0.1"
    
    listener = Listener(address = (ipcasa,6000),authkey = "s")
    print "listener starting"
    manager = Manager()
    messages = manager.dict()
    contacts = manager.dict()
    keys = manager.dict()
    status = manager.dict()
    conexlocales = manager.dict()

    while True:
        print "accepting connections"
	conn = listener.accept()	
	print "connection accepted from",listener.last_accepted
	p = Process(target = serve_client,args = (conn,listener.last_accepted,messages,contacts,keys,conexlocales,status))
	p.start()
	
    listener.close()
	
