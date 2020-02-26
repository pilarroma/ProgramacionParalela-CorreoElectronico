from multiprocessing.connection import Client,Listener
from multiprocessing import Manager,Process
from Tkinter import *

user = ""
password = ""

iplocal = "127.0.0.1"#"147.96.18.188"#"127.0.0.1"#"147.96.18.64"
puertolocal = 4000
passwordlocal = "s"

ipservidor = "127.0.0.1"#"147.96.18.196"#188"#147.96.18.101" #"127.0.0.1"#"147.96.18.64"
ipclase = "147.96.18.188"
#ipclase = "147.96.18.187"
ipcasa ="127.0.0.1"

conn = None

def registration(user,password,addressbook):	
    conn.send([(user,password),"new_user",addressbook]) 	
    return conn.recv()

def connect(user,password):
    global iplocal,passwordlocal,puertolocal,conn
    conn.send([(user,password),"connect",((iplocal,puertolocal),passwordlocal)])
    return conn.recv()

def readmail(user,password):
    conn.send([(user,password),"get_messages"])	
    return conn.recv()

def newmess(user,password,mensaje,destinatario):
    conn.send([(user,password),"send", (destinatario,mensaje)])
    return conn.recv()
   
def addcontact(user,password,contacts):
    conn.send([(user,password),"new_addressbook_contact",contacts]) 
    return conn.recv()

def delcontact(user,password,contacts):
    conn.send([(user,password),"del_addressbook_contact",contacts]) 
    return conn.recv() 
      	
def get_status(user,password):
    conn.send([(user,password),"get_addressbook_status"])
    return conn.recv()

def recvmenchat(notificaChat,mensajechat):
    global iplocal,passwordlocal,puertolocal

    listener = Listener(address = (iplocal,puertolocal),authkey = passwordlocal)

    while True:
        print "accepting connections"
        conexionlocal = listener.accept()	
        mensaje = conexionlocal.recv()
        print "mensajeCHAT",mensaje
        if mensaje[0] =="server_notify_chat":
            mensajechat+=[mensaje[1]]
            print 'mensajePANTALLA',mensajechat  
            notificaChat[0] = True
        else:
            notificaChat[1] = True   

    listener.close()
          
def descon(user,password):
    conn.send([(user,password),"quit"])
    return conn.recv()

def chat(user,password,mens,dest):  
    conn.send([(user,password),"chat",(dest,mens)])
    return conn.recv()

def translista(s):
    i = 0
    lista = []
    while i< len(s):
        c = s[i].rstrip().lstrip()
        if len(c)>0:
            lista.append(c)
        i += 1
    return lista

if __name__ == "__main__":

    m = Manager() 
    notificaChat = m.list([False,False])	
    mensajeChat = m.list([])
    ventana = Tk()
    root = Frame(ventana,bg = "RoyalBlue2")
    root.pack()
    ventana.title("ChatMail RoMaPi")
    Listincontactos = [] 
    vEventos = Frame(root)
    escuchamens = None
    Eventos = StringVar()    #Muestra los eventos

    Eventos.set(" "*20)
    Label(vEventos,textvar = Eventos,bg = "yellow2").pack(side = RIGHT,fill = X)
    vEventos.pack()
    vRegistro = Frame(root,bg = "CadetBlue1")
    

    Label(vRegistro,text = "Usuario:",bg = "violet").grid(row = 0,column = 1)
    Label(vRegistro,text = "key:",bg = "violet").grid(row = 1,column = 1)
    nombusuario = Entry(vRegistro)
    nombusuario.grid(row = 0,column = 2)
    contusuario = Entry(vRegistro)
    contusuario.grid(row = 1,column = 2)
    
    addressbook = Entry(vRegistro)
    addressbook.grid(row = 2,column = 2)
    Label(vRegistro,text = "Listin Contactos:",bg = "violet").grid(row = 2,column = 1)
    Label(vRegistro,text = "(separados por comas)",bg ="violet").grid(row = 2,column = 3)
    
    def registro():
        global conn
        conn = Client(address=(ipservidor,6000),authkey = "s")
        adb = addressbook.get().split(',')
        listacontactos = translista(adb)
        lista = registration(nombusuario.get(),contusuario.get(),listacontactos)
        Eventos.set(lista[1][1])
        addressbook.delete(0,END)
        conn.close()

    def conectarse():
        global escuchamens,conn
 	conn = Client(address=(ipservidor,6000),authkey = "s")
	lista = connect(nombusuario.get(),contusuario.get())
        if lista[1][0]:
      	    Eventos.set(lista[1][1])
            escuchamens = Process(target = recvmenchat, args = (notificaChat,mensajeChat))
            escuchamens.start()
	    enviarstatus()      	
     	else:
            Eventos.set(lista[1][1])
    
    def desconectarse():
        print "desconectando" 
        global escuchamens
        lista = descon(nombusuario.get(),contusuario.get())
        Eventos.set(lista[1][1])
        if lista[1][0]:
            Mensaje.delete("1.0",END)
            vlistin.delete(0,END)
            addressbook.delete(0,END)
            contusuario.delete(0,END)
            MenChat.delete(0,END)#
            EntradaChat.delete("1.0",END)
            vaux2 = Tk()
            vaux2.title("Desconexion") 
            vaux2.geometry("250x60")
            t = Text(vaux2)
            t.insert(END,"\nDESCONEXION CORRECTA.HASTA PRONTO!")
            t.pack()
            escuchamens.terminate()
            conn.close() 
            vaux2.update()
             
    
    def anyadir_contacto():
        adb = addressbook.get().split(',')
        listacontactos = translista(adb)
        print 'l',listacontactos
        respuesta = addcontact(nombusuario.get(),contusuario.get(),listacontactos) 
        print 'res',respuesta
        if len(listacontactos)>0:
         i = 0
         s = ''
         while i<len(respuesta[1]):
          s += listacontactos[i]+respuesta[1][i][1]
          if i<>len(respuesta[1])-1:
            s += '\n'
          i += 1 
        else:                
         s = respuesta[1][0][1]
        Eventos.set(s)
        enviarstatus()
      
    def eliminar_contacto():  
	pos = vlistin.curselection()
      	des = []
      	for p in pos:
            des.append(Listincontactos[int(p)])
        respuesta = delcontact(nombusuario.get(),contusuario.get(),des)
        s = ''
        i = 0
        print respuesta
        if len(des)>0: 
         while i<len(respuesta[1]):
          s += des[i] + respuesta[1][i][1] 
          if i <> len(respuesta[1])-1:
            s += '\n'
          i += 1 
        else:
          s = respuesta[1][0][1] 
        Eventos.set(s)
        enviarstatus()
        
    Button(vRegistro,text = "Registro",command = registro,bg = "turquoise2").grid(row = 0,column = 0)
    Button(vRegistro,text = "Conectarse",command = conectarse,bg = "SpringGreen2").grid(row = 1,column = 0)
    Button(vRegistro,text = "Salir",command = desconectarse,bg = "maroon1").grid(row = 2,column = 0)

    vBotonContactos = Frame(vRegistro)
    Button(vBotonContactos,text = "Anyadir Contacto",command = anyadir_contacto,bg = "MediumOrchid1").grid(row = 0,column = 0)
    Button(vBotonContactos,text = "Eliminar Contacto",command = eliminar_contacto,bg = "yellow").grid(row = 0,column = 1)

    vBotonContactos.grid()
    vRegistro.pack()  
    
    vPpal = Frame(root,bg = "SpringGreen2")
    vUsuario = Frame(vPpal)  
    
    Label(vUsuario,text = "Contactos",bg = "hotpink").pack(fill = X)
    vlistin = Listbox(vUsuario)  
    vlistin.config(selectmode = MULTIPLE)
    vlistin.pack(side = RIGHT,fill = BOTH)

    def enviarstatus():
        global Listincontactos
        respuesta = get_status(nombusuario.get(),contusuario.get())
        vlistin.delete(0,END) 
        for user in respuesta[1][1].keys():
            if respuesta[1][1][user]:
 	        vlistin.insert(END,user+" Conectado")
            else:	
                vlistin.insert(END,user+" Desconectado")
        Listincontactos = respuesta[1][1].keys()

    vUsuario.pack(side = RIGHT)	

    vMail = Frame(vPpal)
    vNuevMens = Frame(vMail,bg = "plum1")
    Mensaje = Text(vNuevMens)
    Mensaje.grid(row = 1 ,column = 1,rowspan = 3,columnspan = 3)
         
    def enviarMensaje():
        pos = vlistin.curselection()
        print 'pos',len(pos)
        if len(pos)==1:
           des = Listincontactos[int(pos[0])]
           print 'DD',des
           print Mensaje.get("1.0",END).rstrip().lstrip()
           respuesta = newmess(nombusuario.get(),contusuario.get(),str(Mensaje.get("1.0",END).rstrip().lstrip()),des)
           print respuesta
           pantalla = str(respuesta[1][1])
           Eventos.set(pantalla)
        elif len(pos)>1:
           Eventos.set('Solo puedes mandar el mensaje a una persona cada vez')
        else:
           Eventos.set('Debes seleccionar a alguien para mandar un mensaje')

    def leerMensaje():
      if nombusuario.get()<>'':#
        mensajes = readmail(nombusuario.get(),contusuario.get()) 
        if mensajes[1][0]:
           vaux = Tk()
           vaux.title("Bandeja de entrada")
           bentrada = ""
           for mensaje in mensajes[1][1]:
              bentrada += "De: "+ mensaje[0]+"\n" + mensaje[1] + "\n"+ "-"*20 +"\n"
           t = Text(vaux) 
           t.insert(END,bentrada)
           t.pack()
           vaux.mainloop()
        else:
           Eventos.set("ERROR.No se puede acceder a la bandeja de entrada") 
      else:#
           Eventos.set("ERROR.No se puede acceder a la bandeja de entrada") 

    def borrarPantallaMensaje():
        textPantalla = Mensaje.get("1.0",END)
        if len(textPantalla.strip())>0:
           Mensaje.delete("1.0",END)
           Eventos.set("Texto borrado")
        else:
           Eventos.set("No hay texto que borrar")
 
    Button(vNuevMens,text = "Enviar Mensaje",command=enviarMensaje,bg = "IndianRed1").grid(row=0,column = 2)
    Button(vNuevMens,text = "Leer Mensajes",command=leerMensaje,bg = "OliveDrab1").grid(row=0,column = 3)
    Button(vNuevMens,text = "Borrar Pantalla",command=borrarPantallaMensaje,bg = "Snow").grid(row = 0,column = 1)

    vNuevMens.pack()
    vMail.pack()

    vPpalChat = Frame(vPpal)
    vChat = Frame(vPpalChat,bg = "CadetBlue1")

    Label(vChat,text = " "*20+"CHAT"+ " "*20,bg = "violet").grid(row = 0 ,column = 0,columnspan = 3)
    EntradaChat = Text(vChat)
    EntradaChat.config(height = 4)
    EntradaChat.grid(row = 1 ,column = 0,rowspan = 3,columnspan = 3)

    vEscritChat = Frame(vPpalChat,bg = "yellow2")
    MenChat = Entry(vEscritChat)

    def enviaChat():
        pos = vlistin.curselection()
        print 'pos',pos
        print len(pos)
        if len(pos)==1:
           des = Listincontactos[int(pos[0])]
           print MenChat.get()
           respuesta = chat(nombusuario.get(),contusuario.get(),MenChat.get(),des)
           print 'RCHAT',respuesta
           EntradaChat.insert(END,"yo: "+ MenChat.get() + '\n')
           Eventos.set(respuesta[1][1]) ##Mostramos por pantalla si ha podido ser enviado
           MenChat.delete(0,END)
        elif len(pos)>1:
           Eventos.set('Solo puedes mandar un mensaje de chat a una persona cada vez')
        else:
           Eventos.set('Debes seleccionar a alguien para mandar un mensaje')
        
    Button(vEscritChat,text = "SEND",command =enviaChat,bg = "DarkSlateGray1").pack(side = RIGHT)	
    MenChat.pack(fill = X)
    
    vChat.pack()
    vEscritChat.pack(fill = X)	
    vPpalChat.pack()
    vPpal.pack()
    
    while True:
        root.update()
        if notificaChat[0]:#Hay mensajes de chat
            bentrada = ""
            print "mChat",mensajeChat
	    for mensaje in mensajeChat:
                print mensaje
                bentrada += mensaje[0]+": " + mensaje[1] + "\n"
                mensajeChat.remove(mensaje)
            EntradaChat.insert(END,bentrada)    
            notificaChat[0] = False 
        if notificaChat[1]:#Alguien se ha conectado
            enviarstatus()
  	    notificaChat[1] = False 
