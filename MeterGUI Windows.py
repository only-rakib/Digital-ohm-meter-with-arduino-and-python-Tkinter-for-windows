from tkinter import *
import sys
import glob
import serial,time
import tkinter.messagebox

comports=""
select=-1
class ArduinoPortsAndData:
  def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class FileHandle:

    def matchLine(lines):
        fh = open("hello.txt", "r")
        for line in fh:
            if line == lines:
                fh.close()
                return line
        return 0

    def get_lines():
        fh = open("hello.txt", "r")
        line = fh.read()
        fh.close()
        return line

    def writeFile(lines):
        fh = open("hello.txt", "w")
        fh.write(lines)
        fh.close()

    def get_lines_port():
        fh = open("port.txt", "r")
        line = fh.read()
        fh.close()
        return line

    def writeFilePort(lines):
        fh = open("port.txt", "w")
        fh.write(lines)
        fh.close()


class PageOneGUI:
    def __init__(self, master):
        self.master = master
        master.title("Rocket Testing-MLRSWS22")
        master.geometry("640x480")

        self.label_rocket_selection = Label(master, text="Rocket Selection",font=('comicsans', 20))
        self.label_rocket_selection.place(x=200,y=50)

        self.v = StringVar()

        self.rg=Radiobutton(master, text="Guided Rkts",font=('Arial', 15), variable=self.v, value= "1")
        self.rg.place(x=200,y=200)
        self.ru=Radiobutton(master, text="Unguided Rkts",font=('Arial', 15), variable=self.v, value= "2")
        self.ru.place(x=200,y=250)
        self.rg.select()
        self.buttonInstraction = Button(master, text="Next", command=self.buttonInstractionFunc)
        self.buttonInstraction.place(x=550,y=400)

    def buttonInstractionFunc(self):
        
        rkts_select=self.v.get()
        FileHandle.writeFile(rkts_select)
        #print(rkts_select)
        if rkts_select=="0":
          tkinter.messagebox.showinfo("Error","Rocket is not selected")
        else:
          self.master.withdraw()
          self.newWindow = Toplevel(self.master)
          bb = PageTwoGUI(self.newWindow)

class PageTwoGUI:
    def __init__(self, master):

        self.master = master
        master.title("Instructions Before Testing")
        master.geometry("650x500")

        self.lst=ArduinoPortsAndData.serial_ports()
        
        self.variable = StringVar()

        self.w = OptionMenu(master, self.variable, *self.lst)#,command=self.print_it)
        self.w.place(x=50,y=20,height=30,width=100)

        Label(master, text="Instructions Before Testing",font=('Arial', 20),fg="red").place(x=200,y=50)
        Label(master, text="1. Rocket test preparation",font=('Arial', 15),fg="blue").place(x=100,y=150)
        Label(master, text="2. Unguided rocket testing",font=('Arial', 15),fg="blue").place(x=100,y=190)
        Label(master, text="3. Guided rocket testing",font=('Arial', 15),fg="blue").place(x=100,y=230)

        self.buttonTesting = Button(master, text="Next", command=self.buttonInstractionFunc)
        self.buttonTesting.place(x=550,y=400)
        
    def buttonInstractionFunc(self):
        global comports

        comports=self.variable.get()
        print(comports)
        if comports=="":
          tkinter.messagebox.showinfo("Error","COM is not selected")
        else:
          self.master.withdraw()
          self.newWindow = Toplevel(self.master)
          bb = PageThreeGUI(self.newWindow)

class PageThreeGUI:
    def __init__(self, master):

        self.master = master
        master.title("Testing")
        master.geometry("650x500")
        global select
        global comports
        #print(comports)
        self.dataAvg=0.0
        self.arduino = serial.Serial(comports, 9600, timeout=.1)
        time.sleep(1) #give the connection a second to settle
        #arduino.write("Hello from Python!")

        if("-m" in sys.argv or "--monitor" in sys.argv):
          monitor = True
        else:
          monitor= False
        i=0
        reading=0.
        while True:
          data=str(self.arduino.readline().decode().strip('\r\n'))
          dataA = data.split("/")
          if data:
            try:
                reading=reading+float(data)
            except:
                tkinter.messagebox.showinfo("Error","Try again")
                #print(paisi,end=' ')
                break
            #print(i)
            i=i+1
          if i>=20:
            dataAvg=reading/i
            break;


        #time.sleep(10)

        self.rkts_select=FileHandle.get_lines()
        self.guidedValue=0.0
        #print(dataAvg)
        if dataAvg>=0.4 and dataAvg<=2.6:
            self.guidedValue=0.6
        elif dataAvg>2.6 and dataAvg<=3.0:
            self.guidedValue=2.2
        else:
            self.guidedValue=4.7

        #Label(master, text=dataAvg,font=('Arial', 20),fg="red").place(x=200,y=200)
        Label(master, text="Guided Rkts",font=('Arial', 20),fg="red").place(x=50,y=50)
        Label(master, text="Unguided Rkts",font=('Arial', 20),fg="red").place(x=50,y=150)
        self.buttonGreenGuided = Label(master,bg ="gray" )
        self.buttonGreenGuided.place(height=30,width=50,x=400,y=50)
        self.buttonRedGuided = Label(master,bg ="gray")
        self.buttonRedGuided.place(height=30,width=50,x=500,y=50)
        self.buttonGreenUnguided = Label(master,bg ="gray")
        self.buttonGreenUnguided.place(height=30,width=50,x=400,y=150)
        self.buttonRedUnguided = Label(master,bg ="gray")
        self.buttonRedUnguided.place(height=30,width=50,x=500,y=150)
        self.w = Text(master,bd=2,height=1,width=12,font=('Arial', 15),fg="red")
        self.w.insert(INSERT,"{0:.3f}".format(self.guidedValue)+" ohm")
        self.w.config(state=DISABLED)
        if self.rkts_select=="1":
            self.w.place(x=250,y=50)
        elif self.rkts_select=="2":
            self.w.place(x=250,y=150)

        if self.rkts_select=="1" and (self.guidedValue<=1.2 and self.guidedValue>=0.4):
            self.buttonGreenGuided.configure(bg ="green")
            self.buttonRedGuided.configure(bg ="gray")
            select=1

        elif self.rkts_select== "1" and (self.guidedValue<0.4 or self.guidedValue>1.2):
            self.buttonRedGuided.configure(bg ="red")
            self.buttonGreenGuided.configure(bg ="gray")
            select=0

        elif self.rkts_select=="2" and (self.guidedValue<=2.75 and self.guidedValue>=1.75):
            self.buttonGreenUnguided.configure(bg ="green")
            self.buttonRedUnguided.configure(bg ="gray")
            select=1

        elif self.rkts_select== "2" and (self.guidedValue<1.75 or self.guidedValue>2.75):
            self.buttonRedUnguided.configure(bg ="red")
            self.buttonGreenUnguided.configure(bg ="gray")
            select=0
        else:
          self.buttonGreenGuided.configure(bg ="gray")
          self.buttonRedGuided.configure(bg ="gray")
          self.buttonRedUnguided.configure(bg ="gray")
          self.buttonGreenUnguided.configure(bg ="gray")
          select=-1
        #self.close_button = Button(master, text="Close", command=master.quit)
        #self.close_button.pack()

        self.buttonTesting = Button(master, text="Next", command=self.buttonInstractionFunc)
        self.buttonTesting.place(x=550,y=400)

    def buttonInstractionFunc(self):
        self.master.withdraw()
        self.newWindow = Toplevel(self.master)
        bb = PageFourGUI(self.newWindow)
class PageFourGUI:
    def __init__(self, master):

        self.master = master
        master.title("Result")
        master.geometry("650x500")
        global select
        self.rkts_select=FileHandle.get_lines()

        Label(master, text="Result",font=('Arial', 20),fg="red").place(x=200,y=50)
        Label(master, text="1. Testing completed",font=('Arial', 15),fg="blue").place(x=100,y=150)

        if self.rkts_select=="1" and select==1:
            Label(master, text="2. Guided rocket is QC Passed",font=('Arial', 15),fg="blue").place(x=100,y=190)
            Label(master, text="3. Rkts is ready to fire",font=('Arial', 15),fg="blue").place(x=100,y=230)

        elif self.rkts_select== "1" and select==0:
            Label(master, text="2. Guided rocket is not QC Passed",font=('Arial', 15),fg="blue").place(x=100,y=190)
            Label(master, text="3. Rkts is not ready to fire",font=('Arial', 15),fg="blue").place(x=100,y=230)

        elif self.rkts_select=="2" and select==1:
            Label(master, text="2. Unguided rocket is QC Passed",font=('Arial', 15),fg="blue").place(x=100,y=190)
            Label(master, text="3. Rkts is ready to fire",font=('Arial', 15),fg="blue").place(x=100,y=230)
        elif self.rkts_select== "2" and select==0:
            Label(master, text="2. Unuided rocket is not QC Passed",font=('Arial', 15),fg="blue").place(x=100,y=190)
            Label(master, text="3. Rkts is not ready to fire",font=('Arial', 15),fg="blue").place(x=100,y=230)

        else:
            Label(master, text="No rocket selected",font=('Arial', 15),fg="blue").place(x=100,y=150)

        self.buttonTesting = Button(master, text="Exit",command=master.quit)
        self.buttonTesting.place(x=550,y=400)
        #self.close_button = Button(master, text="Close", command=master.quit)
        #self.close_button.pack()


if __name__ == '__main__':
    root = Tk()
    b = PageOneGUI(root)
    root.mainloop()

