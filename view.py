from time import sleep
from hexdump import hexdump
from locale import format
import tkinter as tk
from _tkinter import TclError
from syntaxtext import SyntaxText
from os.path import basename

class View:
    def __init__(self, controller):
        self.controller = controller

    def schritt(self):
        pass

    def rechner_eingabe(self):
        return 0

    def rechner_ausgabe(self, n):
        pass



class PIOEingabeDialog:
    def __init__(self, parent, port):
        self.parent = parent
        top = self.top = tk.Toplevel(parent)
        top.title("PIO-Eingabe")
        top.resizable(False, False)
        tk.Label(top, text="Port: "+str(port)+"\nWert:").pack()
        self.e = tk.Entry(top)
        self.e.pack(padx=5)
        b = tk.Button(top, text="OK", command=self.ok)
        b.pack(pady=5)
        self.wert = None

    def ok(self):
        eingabe = self.e.get()
        if (eingabe.isnumeric()):
            self.wert = int(eingabe)
        else:
            self.wert = ord(eingabe[0])
        self.top.destroy()

    def warte(self):
        self.parent.wait_window(self.top)
        return self.wert


class RechnerDiagramm(tk.Canvas):
    def __init__(self, parent, schriftart = "Helvetica"):
        w, h = 800, 560
        tk.Canvas.__init__(self, parent, bg = "#FFFFFF", width = w, height = h, confine = True, scrollregion = (0, 0, w, h))
        self.schriftart = schriftart
        
        # Rechen- und Steuerwerk
        self.create_rectangle(0, 0, 350, h, fill = "#E6E6E6")
        self.create_text(175, 25, text = "Rechen- und Steuerwerk", font = self.schriftart+" 16 bold")
        register = [("AKKU", "Akkumulator",       (193, 153)),
                    ("ER",   "Ergebnisregister",  (193, 414)),
                    ("BZ",   "Befehlszeiger",     (17,  73)),
                    ("BR",   "Befehlsregister",   (17,  153)),
                    ("SZ",   "Stapelzeiger",      (17,  233)),
                    ("SB",   "Stapelbasiszeiger", (17,  312)),
                    ("XR",   "Indexregister",     (193, 233)),
                    ("AR",   "Adressregister",    (193, 494)),
                    ("DR",   "Datenregister",       (193, 73))]
        self.register = {}
        for reg in register:
            self.register[reg[0]] = self.create_register(reg[2][0], reg[2][1], reg[1])
        self.create_rectangle(193, 312, 322, 380, fill = "#FFFFFF")
        self.create_text(257, 346, text = "Arithmetische\nLogik-Einheit", font = self.schriftart+" 12 bold")

        # Speicher
        self.create_rectangle(350, 80, 650, 490, fill = "#E6E6E6")
        self.create_text(500, 105, text = "Speicher (RAM)", font = self.schriftart+" 16 bold")
        self.lst_speicher = tk.Listbox(parent, activestyle = "dotbox", exportselection = 0, bg = "#FFFFFF", selectbackground = "#FFFF00", selectforeground = "#000000", font = self.schriftart+" 12", selectmode = "single")
        self.scy_speicher = tk.Scrollbar(parent, command = self.lst_speicher.yview)
        self.lst_speicher.config(yscrollcommand = self.scy_speicher.set)
        self.create_window(355, 130, width = 270, height = 355, window = self.lst_speicher, anchor = "nw")
        self.create_window(625, 130, width = 20, height = 355, window = self.scy_speicher, anchor = "nw")

        # Peripherie
        self.create_rectangle(650, 80, w, 490, fill = "#E6E6E6")
        self.create_text(725, 105, text = "Peripherie", font = self.schriftart+" 16 bold")
        self.eingabe = self.create_register(665, 143, "Eingabe")
        self.ausgabe = self.create_register(665, 223, "Ausgabe")

        # Pfeile
        self.create_line(146, 99, 193, 99)
        self.create_line(146, 179, 193, 179)
        self.create_line(146, 259, 193, 259)
        self.create_line(146, 339, 169, 339, 169, 346, 193, 346, arrow = "last")
        self.create_line(169, 99, 169, 525, 193, 525, arrow = "last")
        self.create_line(322, 89, 335, 89, 335, 50, 725, 50, 725, 80, arrow = "both")
        self.create_line(500, 50, 500, 80, arrow = "last")

        self.create_line(322, 179, 335, 179, 335, 259, arrow = "last")
        self.create_line(322, 259, 335, 259, 335, 295, 257, 295, 257, 312, arrow = "last")
        self.create_line(257, 380, 257, 414, arrow = "last")
        self.create_line(322, 440, 335, 440, 335, 480, 169, 480, arrow = "last")

        self.create_line(322, 520, 335, 520, 335, 540, 725, 540, 725, 490, arrow = "last")
        self.create_line(500, 540, 500, 490, arrow = "last")

    def create_register(self, x, y, name, wert = ""):
        w, h = 129, 49
        self.create_rectangle(x, y, x+w, y+h, fill = "#CCCCCC")
        self.create_text(x+int(w/2), y+int(h/4), text = name+":", font = self.schriftart+" 10 bold")
        return self.create_text(x+int(w/2), y+int(3*h/4), text = str(wert), font = self.schriftart+" 10")

    def set_register(self, reg, wert = ""):
        self.itemconfigure(self.register[reg], text = wert)

    def set_eingabe(self, port, wert = ""):
        self.itemconfigure(self.eingabe, text = str(port)+": "+str(wert))

    def set_ausgabe(self, port, wert = ""):
        self.itemconfigure(self.ausgabe, text = str(port)+": "+str(wert))

    def set_speicher(self, rechner, asmhints = None):
        def cmd(a):
            if (asmhints!=None):
                if (a in asmhints):
                    return " ("+asmhints[a]+")"
            return ""

        self.lst_speicher.delete(0, "end")        
        self.lst_speicher.insert(0, *[str(i).zfill(4)+": "+str(rechner.speicher[i]).zfill(3)+cmd(i) for i in range(len(rechner.speicher))])
        self.lst_speicher.activate(rechner.register["BZ"])
        self.lst_speicher.selection_set(rechner.register["BZ"])
        self.lst_speicher.yview_scroll(rechner.register["BZ"], "units")

class ViewGUI(View):
    filetypes = [("Assembler-Code", "*.asm"), ("Text-Datei", "*.txt")]
    
    def __init__(self, controller):
        View.__init__(self, controller)

        # Lade Hilfe zu Befehlen
        # TODO aus Datei laden
        self.max_taktrate = 5
        self.schriftart = "helvetica"
        self.schriftgröße = 10
        #self.befehle = {"LDAD": ("n", "Lädt n in Akkumulator")}
        self.befehle = eval(open("befehle.txt").read(-1), {"__builtins__": None})
        
        # Hauptfenster
        self.haupt = tk.Tk()
        self.dateiname = None
        self.setze_titel()
        self.haupt.protocol("WM_DELETE_WINDOW", self.beende)
        self.haupt.resizable(True, True)
        try:
            self.haupt.iconbitmap(default = "gui.ico")
        except TclError:
            pass
        self.haupt.rowconfigure(1, weight = 1)
        self.haupt.columnconfigure(0, weight = 1)

        menü = tk.Menu(self.haupt)
        menü_datei = tk.Menu(menü)
        menü_datei.add_command(label = "Neu", command = self.menü_datei_neu)
        menü_datei.add_command(label = "Öffnen", command = self.menü_datei_öffnen)
        menü_datei.add_command(label = "Speichern", command = self.menü_datei_speichern)
        menü_datei.add_command(label = "Speichern unter", command = self.menü_datei_speichern_unter)
        menü_datei.add_command(label = "Beenden", command = self.beende)
        menü.add_cascade(label = "Datei", menu = menü_datei)
        menü_bearbeiten = tk.Menu(menü)
        menü_bearbeiten.add_command(label = "Rückgängig", command = self.menü_bearbeiten_rückgängig)
        menü_bearbeiten.add_command(label = "Wiederherstellen", command = self.menü_bearbeiten_wiederherstellen)
        menü_bearbeiten.add_command(label = "Ausschneiden", command = self.menü_bearbeiten_ausschneiden)
        menü_bearbeiten.add_command(label = "Kopieren", command = self.menü_bearbeiten_kopieren)
        menü_bearbeiten.add_command(label = "Einfügen", command = self.menü_bearbeiten_einfügen)
        menü.add_cascade(label = "Bearbeiten", menu = menü_bearbeiten)
        menü_rechner = tk.Menu(menü)
        menü_rechner.add_command(label = "Starten", command = self.menü_rechner_starten)
        menü.add_cascade(label = "Rechner", menu = menü_rechner)
        menü_hilfe = tk.Menu(menü)
        menü_hilfe.add_command(label = "Über", command = self.menü_hilfe_über)
        menü.add_cascade(label = "Hilfe", menu = menü_hilfe)
        self.haupt.config(menu = menü)
        
        self.lbl_programm_code = tk.Label(self.haupt, text = "Programm-Code")
        self.lbl_programm_code.grid(row = 0, column = 0, sticky = "W")

        self.txt_code = SyntaxText(self.haupt, wrap = "none", bg = "#FFFFFF", schriftgröße = self.schriftgröße, schriftart = self.schriftart, befehle = list(self.befehle))
        self.scy_code = tk.Scrollbar(self.haupt, command = self.txt_code.yview)
        self.scx_code = tk.Scrollbar(self.haupt, command = self.txt_code.xview, orient = "horizontal")
        self.txt_code.config(yscrollcommand = self.scy_code.set, xscrollcommand = self.scx_code.set)
        self.scx_code.grid(row = 6, column = 0, sticky = "EW")
        self.scy_code.grid(row = 1, column = 1, rowspan = 5, sticky = "NS")
        self.txt_code.grid(row = 1, column = 0, rowspan = 5, sticky = "NSEW")

        self.lst_befehle = tk.Listbox(self.haupt, activestyle = "dotbox", exportselection = 0, bg = "#FFFFFF")
        self.scy_befehle = tk.Scrollbar(command = self.lst_befehle.yview)
        self.lst_befehle.config(yscrollcommand = self.scy_befehle.set)
        self.lst_befehle.insert("end", *list(sorted(self.befehle)))
        self.scy_befehle.grid(row = 1, column = 3, rowspan = 5, sticky = "NS")        
        self.lst_befehle.grid(row = 1, column = 2, rowspan = 5, sticky = "NSEW")
        self.lst_befehle.bind('<ButtonRelease-1>', self.befehl_anzeigen)
        self.lst_befehle.bind('<Return>', self.befehl_einfügen)

        self.lbl_befehl = tk.Label(self.haupt, text = "", width = 30, justify = "left")
        self.lbl_befehl.grid(row = 1, column = 4, sticky = "NW")
        self.lbl_befehl_erklärung = tk.Label(self.haupt, text = "n: Natürliche Zahl\na: Adresse\nU: unmittelbar\nD: direkt\nI: indirekt", justify = "left")
        self.lbl_befehl_erklärung.grid(row = 2, column = 4, sticky = "NW")
        
        # Rechner-Fenster
        self.rechner = tk.Toplevel(self.haupt)
        self.rechner.withdraw()
        self.rechner.title("Simulation - Von-Neumann-Rechner")
        self.rechner.protocol("WM_DELETE_WINDOW", self.rechner_beenden)
        self.rechner.rowconfigure(1, weight = 1)
        self.rechner.columnconfigure(4, weight = 1)
        self.rechner.resizable(False, False)

        self.img_schritt = tk.PhotoImage(file = "buttons/schritt.gif")
        self.btn_schritt = tk.Button(self.rechner, command = self.rechner_schritt, text = "Schritt", image = self.img_schritt)
        self.btn_schritt.grid(row = 0, column = 0, sticky = "NSW")
        self.img_start = tk.PhotoImage(file = "buttons/start.gif")
        self.btn_start = tk.Button(self.rechner, command = self.rechner_start, image = self.img_start)
        self.btn_start.grid(row = 0, column = 1, sticky = "NSW")
        self.img_pause = tk.PhotoImage(file = "buttons/pause.gif")
        self.btn_pause = tk.Button(self.rechner, command = self.rechner_pause, image = self.img_pause)
        self.btn_pause.grid(row = 0, column = 2, sticky = "NSW")
        self.img_stop = tk.PhotoImage(file = "buttons/stop.gif")
        self.btn_stop = tk.Button(self.rechner, command = self.rechner_beenden, image = self.img_stop)
        self.btn_stop.grid(row = 0, column = 3, sticky = "NSW")

        self.diagramm = RechnerDiagramm(self.rechner)
        self.diagramm.grid(row = 1, column = 0, columnspan = 5, sticky = "NSWE")

    def setze_schriftart(self, art, größe):
        self.txt_code.setze_schriftart(art, größe)

    def befehl_anzeigen(self, event):
        b = self.lst_befehle.get(self.lst_befehle.curselection()[0])
        befehl = self.befehle[b]
        self.lbl_befehl.config(text = b+" "+befehl[0]+"\n"+befehl[1])

    def befehl_einfügen(self, event):
        b = self.lst_befehle.get(self.lst_befehle.curselection()[0])
        self.txt_code.insert("insert", b+" ")
        self.txt_code.changed()

    def setze_titel(self):
        if (self.dateiname==None):
            self.haupt.title("Von-Neumann-Rechner")
        else:
            self.haupt.title(basename(self.dateiname)+" - Von-Neumann-Rechner")

    def beende(self):
        self.haupt.destroy()
        self.controller.beende()
        
    def schritt(self):
        self.haupt.update()

    def menü_datei_neu(self):
        self.dateiname = None
        self.txt_code.delete(1.0, "end")
        self.txt_code.changed()
        self.setze_titel()

    def menü_datei_öffnen(self):
        dateiname = tk.filedialog.askopenfilename(parent = self.haupt,
                                                  title = "Datei öffnen",
                                                  defaultextension = ".asm",
                                                  filetypes = self.filetypes,
                                                  initialdir = "programme/")
        if (dateiname!=""):
            try:
                f = open(dateiname)
                code = f.read(-1)
                f.close()

                self.dateiname = dateiname
                self.setze_titel()
                self.txt_code.delete("1.0", "end")
                self.txt_code.insert("1.0", code)
                self.txt_code.changed()
            except IOError:
                tk.messagebox.showerror("Fehler", "Konnte Datei '"+dateiname+"' nicht öffnen.")
        
    def datei_speichern(self, datei):
        print("Datei speichern: "+str(datei))
        if (type(datei)==str):
            dateiname = datei
            try:
                f = open(dateiname, "w")
            except:
                tk.messagebox.showerror("Fehler", "Konnte Datei '"+dateiname+"' nicht öffnen.")
                return False
        else:
            dateiname = datei.name
            f = datei

        f.write(self.txt_code.get(1.0, "end"))
        f.close()

        self.dateiname = dateiname
        self.setze_titel()
        return True

    def menü_datei_speichern(self):
        # TODO bei jedem Speichern Unter wird am Ende eine neue Zeile hinzugefügt. Warum?
        if (self.dateiname==None):
            self.menü_datei_speichern_unter()
        else:
            self.datei_speichern(self.dateiname)

    def menü_datei_speichern_unter(self):
        datei = tk.filedialog.asksaveasfile(parent = self.haupt,
                                            title = "Datei speichern",
                                            defaultextension = ".asm",
                                            filetypes = self.filetypes,
                                            initialdir = "programme/")
        self.datei_speichern(datei)

    def menü_bearbeiten_rückgängig(self):
        self.txt_code.edit_undo()

    def menü_bearbeiten_wiederherstellen(self):
        self.txt_code.edit_redo()

    def menü_bearbeiten_ausschneiden(self):
        self.txt_code.event_generate("<<Cut>>")

    def menü_bearbeiten_kopieren(self):
        self.txt_code.event_generate("<<Copy>>")

    def menü_bearbeiten_einfügen(self):
        self.txt_code.event_generate("<<Paste>>")

    def menü_rechner_starten(self):
        self.controller.erzeuge_rechner()
        try:
            self.asmhints = self.controller.lade_programm(self.txt_code.get(1.0, "end"))
            self.rechner_zeige_status()
            self.rechner.deiconify()
            self.rechner.lift(self.haupt)
        except (SyntaxError, RuntimeError) as e:
            self.programm_fehler(e)

    def menü_hilfe_über(self):
        über = "Von-Neumann-Rechner "+self.controller.version+"\n"+\
               "von Janosch Gräf <janosch.graef@gmx.net>\n\n"+\
               "Dieses Programm simuliert einen einfachen Computer nach der von-Neumann-Architektur"
        tk.messagebox.showinfo("Über Von-Neumann-Rechner", über, parent = self.haupt)

    def programm_fehler(self, e):
        if (type(e)==SyntaxError):
            tk.messagebox.showerror("Syntax-Fehler", str(e), parent = self.haupt)
        else:
            tk.messagebox.showerror("Fehler", str(e), parent = self.haupt)

    def rechner_eingabe(self, p):
        wert = PIOEingabeDialog(self.rechner, p).warte()
        self.diagramm.set_eingabe(p, wert)
        return wert


    def rechner_ausgabe(self, p, wert):
        self.diagramm.set_ausgabe(p, wert)
        tk.messagebox.showinfo("PIO-Ausgabe", "Port "+str(p)+":\n"+str(wert), parent = self.rechner)

    def rechner_beenden(self):
        self.rechner.withdraw()
        self.controller.zerstöre_rechner()

    def rechner_schritt(self):
        self.controller.rechner.schritt()
        self.rechner_zeige_status()

    def rechner_start(self):
        pass

    def rechner_pause(self):
        pass

    def rechner_zeige_status(self):
        r = self.controller.rechner
        d = self.diagramm

        for reg in d.register:
            if (reg=="BR" and r.register[reg] in r.befehle):
                d.set_register(reg, r.befehle[r.register[reg]][0])
            else:
                d.set_register(reg, str(r.register[reg]))

        d.set_speicher(r, self.asmhints)

    
class ViewText(View):
    def zeige_status(self):
        print("Register:")
        for name in self.controller.rechner.register:
            wert = self.controller.rechner.register[name]
            if (name=="BR"):
                wert = self.controller.rechner.befehle[wert][0]
            else:
                wert = "0x"+format("%02X", wert)
            print("  "+name+": "+str(wert))

    def zeige_speicher(self, start = 0, n = None):
        if (n==None):
            n = len(self.controller.rechner.speicher)
        print(hexdump(self.controller.rechner.speicher[start:start+n], start))

    def schritt(self):
        befehl = input("> ").split()
        if (befehl==[] or befehl[0]=="schritt"):
            if (self.controller.rechner!=None):
                self.controller.rechner.schritt()
                self.zeige_status()
            else:
                print("Rechner muss zuerst erzeugt werden.")
        elif (befehl[0]=="erzeuge"):
            self.controller.erzeuge_rechner()
        elif (befehl[0]=="zerstöre"):
            self.controller.zerstäre_rechner()
        elif (befehl[0]=="lade"):
            self.controller.lade_datei(befehl[1])
        elif (befehl[0]=="beende"):
            self.controller.beende()
        elif (befehl[0]=="status"):
            if (self.controller.rechner!=None):                
                self.zeige_status()
            else:
                print("Rechner muss zuerst erzeugt werden.")
        elif (befehl[0]=="speicher"):
            if (self.controller.rechner!=None):                
                self.zeige_speicher()
            else:
                print("Rechner muss zuerst erzeugt werden.")
        else:
            print("Unbekannter Befehl: "+befehl[0]+".")

    def rechner_eingabe(self, p):
        while (True):
            try:
                return int(input("Eingabe[port="+str(p)+"]: "))
            except TypeError:
                print("Value must be string")

    def rechner_ausgabe(self, p, n):
        print("Ausgabe[port="+str(p)+"]: "+str(n))
