#! /usr/bin/python
#
#	buscaminas.py
#	Implementacion en Python del famoso juego Buscaminas inventado por Robert Donner en 1989.
#
#	Copyleft 2008-2010  Qcho
#
#	Este programa es software libre: usted puede redistribuirlo y/o modificarlo conforme a los terminos de la Licencia Publica General de GNU publicada
#	por la Fundacion para el Software Libre, ya sea la version 3 de esta Licencia o (a su eleccion) cualquier version posterior.
#	Este programa se distribuye con el deseo de que le resulte util, pero SIN GARANTIAS DE NINGUN TIPO; ni siquiera con las garantias implicitas de
#	COMERCIABILIDAD o APTITUD PARA UN PROPOSITO DETERMINADO.  Para mas informacion, consulte la Licencia Publica General de GNU.
#	Junto con este programa, se deberia incluir una copia de la Licencia Publica General de GNU.
#	De no ser asi, ingrese en <http://www.gnu.org/licenses/>.
#
from Tkinter import *
import tkMessageBox
import random
from platform import uname as OS

# Reproduce un determinado sonido de tipo wav (file) reconociendo en que plataforma esta trabajando (Windows/Linux).
def playSnd(file):
    try:
        if OS()[0]=='Windows':
            from winsound import PlaySound, SND_ASYNC
            PlaySound(file, SND_ASYNC)
        elif OS()[0]=='Linux':
            from wave import open as waveOpen
            from ossaudiodev import open as ossOpen
            s = waveOpen(file,'rb')
            (nc,sw,fr,nf,comptype, compname) = s.getparams( )
            dsp = ossOpen('/dev/dsp','w')
            try:
                from ossaudiodev import AFMT_S16_NE
            except ImportError:
                if byteorder == "little":
                    AFMT_S16_NE = ossaudiodev.AFMT_S16_LE
                else:
                    AFMT_S16_NE = ossaudiodev.AFMT_S16_BE
            dsp.setparameters(AFMT_S16_NE, nc, fr)
            data = s.readframes(nf)
            s.close()
            dsp.write(data)
            dsp.close()
    except:
        print " (Error: No se pudo reproducir el sonido)"

# Devuelve un array de los puntajes almacenados en el texto plano determinado.
def obtenerRecords():
    recAux={}
    keys=[]
    values=[]
    rs=open("BMimgs/records","r")
    for linea in rs.readlines():
        if linea<>"":
            x=linea.split("\t")
            keys.append(float(x[1]))
            values.append(x[0])
    rs.close()
    recAux=recAux.fromkeys(keys)
    cont=0
    for key in keys:
        recAux[key]=values[cont]
        cont+=1
    keys.sort()
    keys.reverse()
    records=""
    for key in keys:
        records+=recAux[key]+"\t"+`key`+"\n"
    return records[:-1]
    
# Rebibe un nombre y una puntuacion (score) para registrarlos en el texto plano determinado.
def grabarRecord(nombre,score):
    z=obtenerRecords()
    rx=open("BMimgs/records","w")
    rx.write(z+"\n"+nombre+"\t"+`score`)
    rx.close()
    
# Recibe una ventana de tipo Tkinter (vent), y todos los datos adicionales para crear un campo (mediante__init__).
class BuscaminasGUI:
    def __init__(self,vent,nom,alto,ancho,numMinas):
	# definicion de imagenes usadas en el juego.
        imgCaraBien = PhotoImage(file="BMimgs/cara_ok.gif")
        imgCaraMal = PhotoImage(file="BMimgs/cara_mal.gif")
        imgCaraSeria = PhotoImage(file="BMimgs/cara.gif")
        imgMina = PhotoImage(file="BMimgs/mina.gif")
        imgBoom = PhotoImage(file="BMimgs/boom.gif")
        imgBloq = PhotoImage(file="BMimgs/bloq.gif")
	# definicion de las 3 etiquetas informativas (bloqueos, estado y tiempo).
        lblEstado=Label(image=imgCaraSeria, relief=RIDGE, borderwidth=3)
        lblBloqueos=Label(font=("Courier",12), relief=RIDGE, borderwidth=3)
        lblTiempo=Label(text="0",font=("Courier",12), relief=RIDGE, borderwidth=3)
	# ubicacion de las 3 etiquetas informativas en el tablero.
        lblBloqueos.grid(row=0,column=0,columnspan=int(ancho/3))
        lblEstado.grid(row=0,column=0,columnspan=(ancho))
        lblTiempo.grid(row=0,column=((2*ancho/3)+1),columnspan=(ancho/3))
        self.casillas = []
        self.numCasillas=alto*ancho
        
	# Inicializa el campo cuando se crea o resetea.
        def setCampo():
            self.termino=0
            contar()
            self.restantes = self.numCasillas-numMinas
            lblEstado["image"]=imgCaraSeria
            self.nbloq=numMinas
            lblBloqueos["text"]=`self.nbloq`
            lblTiempo["text"]=`0`
            for elemento in self.casillas:
                elemento.destroy()
            del self.casillas
            self.casillas=[]
            self.minas=random.sample(range(self.numCasillas),numMinas)
            for i in range(self.numCasillas):
                casilla = Label(vent, text="   ", font=("Courier",10,"bold"), relief=RIDGE, borderwidth=1)
                self.casillas.append(casilla)
                def click (event, self=self, i=i):
                    marcar(i)
                casilla.bind('<Button-1>',click)
                def clickder (event, self=self, i=i):
                    bloquear(i)
                casilla.bind('<Button-3>',clickder)
                r=int(i/ancho)+1
                casilla.grid(row=r,column=i%ancho)
                
	# Devuelve el array con las casillas alrededor a una casilla z.
        def contorno(z):
            con=[z-1-ancho,z-ancho,z+1-ancho,z-1,z+1,z-1+ancho,z+ancho,z+1+ancho]
            for item in range(8):
                aux=con[item]
                if not 0<=aux<self.numCasillas:
                    con[item]=None
                elif z%ancho==0 and (aux+1)%ancho==0:
                    con[item]=None
                elif (z+1)%ancho==0 and aux%ancho==0:
                    con[item]=None
            return con
            
	# Devuelve el numero de minas alrededor a una casilla m.
        def numCont(m):
            count=0
            for min in contorno(m):
                if min in self.minas:
                    count+=1
            return count
            
	# Devuelve un color especifico para determinada cantidad de minas.
        def color(i):
            if i==1:
                return "blue"
            elif i==2:
                return "orange"
            elif i==3:
                return "red"
            elif i==4:
                return "darkgreen"
            elif i==5:
                return "purple"
            elif i==6:
                return "cyan"
            elif i==7:
                return "magenta"
            elif i==8:
                return "brown"
            else:
                return "darkgrey"
                
	# Despliega una ventana con las mejores puntuaciones.
        def listaRecords():
            tkMessageBox.showinfo("Records", obtenerRecords())
            
	# Reproduce el sonido cuando se toca una bomba.
        def playPerdiste():
            playSnd("BMimgs/boom.wav")
            
	# Reproduce el sonido cuando se gana y registra la puntuacion.
        def playGanaste():
            playSnd("BMimgs/gong.wav")
            score=float(alto*ancho*numMinas/float(lblTiempo["text"]))
            if tkMessageBox.askyesno("Ganador", "Felicidades, "+nom+"!!!\nTu Puntaje es: "+`score`+"\nDeseas Guardarlo?"):
                grabarRecord(nom,score)
                listaRecords()
            else:
                tkMessageBox.showinfo("No guardado", "Haz escogido no guardar tu Puntaje")  
                
	# Abre la casilla en la posicion pos cuando se le da un click izquierdo encima.
        def marcar(pos):
            if self.termino==0 and self.casillas[pos]["text"]=="   ":
                self.casillas[pos]["borderwidth"]=2
                if pos in self.minas:
                    lblEstado["image"]=imgCaraMal
                    for bomba in self.minas:
                        if bomba==pos:
                            self.casillas[bomba]["image"]=imgBoom
                        elif self.casillas[bomba]["text"]==" ! ":
                            self.casillas[bomba]["image"]=imgBloq
                        else:
                            self.casillas[bomba]["image"]=imgMina
                    self.termino=1
                    playPerdiste()
                else:
                    self.restantes-=1
                    al=numCont(pos)
                    self.casillas[pos]["text"]=" "+`al`+" "
                    self.casillas[pos]["fg"]=color(al)
                    self.casillas[pos]["bg"]="darkgrey"
                    if  al==0:
                        for posi in contorno(pos):
                            if posi<>None:
                                marcar(posi)
                    if self.restantes==0:
                        for bomba in self.minas:
                            self.casillas[bomba]["image"]=imgBloq
                        lblEstado["image"]=imgCaraBien
                        self.termino=1
                        playGanaste()
                        
	# Bloquea/desbloquea la casilla en la posicion pos cuando se le da un click derecho encima.
        def bloquear(pos):
            if self.termino==0:
                if self.casillas[pos]["text"]==" ! ":
                    self.casillas[pos]["text"]="   "
                    self.nbloq+=1
                elif self.casillas[pos]["text"]=="   " and self.nbloq>0:
                    self.nbloq-=1
                    self.casillas[pos]["text"]=" ! "
                    self.casillas[pos]["fg"]="darkred"
                lblBloqueos["text"]=`self.nbloq`
                
	# Reinicia el tiempo y el campo ya creado.
        def reset(event):            
            lblTiempo.after_cancel(self.idaf)
            setCampo()
            
	# Activa un bucle para aderir unidades al contador de tiempo en una unidad cada segundo (activa el contador de tiempo).
        def contar():
            if self.termino==0:
                lblTiempo["text"]=`int(lblTiempo["text"])+1`
                self.idaf = lblTiempo.after(1000, contar)
                
	# Bloquea/desbloquea el campo y detiene/reanuda el contador de tiempo del juego (pausa el juego) a peticion del jugador.
        def pausa(event):
            if self.termino==0:
                self.termino=2
                tkMessageBox.showwarning("Pausa", "Juego Pausado\nPulse OK para volver")
                self.termino=0
                contar()
                
	# Llama a listaRecords a peticion del jugador.
        def mostrarListaRecords(event):
                 listaRecords()
                 
	# Depliega una advertencia si el jugador desea abandonar el juego y cierra/vuelve al juego.
        def cerrar():
            z=self.termino
            self.termino=2
            if tkMessageBox.askyesno("Abandonar", "En realidad desea abandonar?"):
                lblTiempo.after_cancel(self.idaf)
                vent.destroy()
            else:
                self.termino=z
                contar()
	# definicion de eventos a usar al dar click sobre las 3 etiquetas informativas (bloqueos, estado y tiempo).
        lblEstado.bind('<Button-1>',reset)
        lblTiempo.bind('<Button-1>',pausa)
        lblBloqueos.bind('<Button-1>',mostrarListaRecords)
	# definicion de evento al cerrar.
        vent.protocol("WM_DELETE_WINDOW", cerrar)
	# inicio del campo al llamar a la clase.
        setCampo()
        
# Determina si un valor a ingresado se encuentra entre el rango daterminado (min,max).
def inputVal(a,min,max):
    try:
        x=int(raw_input(a))
        if min<=x<=max:
            return x;
        else:
            return inputVal("  (Debe estar entre "+`min`+" y "+`max`+"): ",min,max)
    except:
        return inputVal("  (Debe ser un numero entre "+`min`+" y "+`max`+"): ",min,max)
        
# Determina si un nombre a ingresado es valido.
def inputNom(a):
    try:
        x=raw_input(a).strip("\n").strip()
        if x=="":
            return inputVal("  (No puede ser cadena vacia): ")
        else:
            return x
    except:
        return inputVal("  (Error! Reintente): ")
        
# Devuelve un booleano en relacion con el valor que se solicita despues de presentar una cadena a dada.
def inputSiNo(a):
    try:
        if raw_input(a+" [s/n]: ")=="s":
            return True
        else:
            return False
    except:
        print "Fin de Programa"
        return False
        
# Recupera los datos necesarios para la creacion de un campo, define una ventana y llama a la clase que construira el entorno grafico.
def buscaminas(nom,alto,ancho,nb):
    vent=Tk()
    BuscaminasGUI(vent,nom,alto,ancho,nb)
    vent.title("Buscaminas")
    vent.mainloop()
    if inputSiNo("Desea rehacer el campo con otras dimensiones?"):
        jugar()
    else:
        raw_input("Gracias por jugar!");
        
# Empieza con la creacion del buscaminas, es llamado al inicio y cada vez que se solicita re-crear el campo.
def jugar():
    nombre=inputNom("Ingrese su nombre: ")
    ancho=inputVal("Ingrese el ancho del campo (en cuadros): ",4,25)
    min=10
    max=100
    if ancho >4:
        min+=10
        max+=50
    if ancho >8:
        min+=15
        max+=60
    if ancho >12:
        min+=20
        max+=70
    if ancho >15:
        min+=25
        max+=30
    alto=inputVal("Ingrese el alto del campo (en cuadros): ",int(min/ancho),int(max/ancho))
    c=pow((ancho*alto),0.5)
    b=inputVal("Ingrese el # de minas que desea buscar: ",int(pow(c,0.9)),int(pow(c,1.5)))
    buscaminas(nombre,alto,ancho,b)
    
# Ejecucion del juego:
print ("--------------------------------------------------------------------\nBuscaminas v 0.5\nCopyleft 2008-2010 Qcho\n\tEste programa es software libre y usted puede redistribuirlo\n\t conforme a ciertas condiciones.\n--------------------------------------------------------------------\n")
jugar()
