from von_neumann import VonNeumannRechner
from assembler import Assembler
from view import ViewText, ViewGUI
from configparser import SafeConfigParser as ConfigParser

class Controller:
    version = "0.1.0001"
    
    def __init__(self, textmodus = False):
        self.rechner = None
        self.speichergröße = 512
        self.max_taktrate = 5
        self.schriftgröße = 10
        if (textmodus):
            self.view = ViewText(self)
        else:
            self.view = ViewGUI(self)

    def erzeuge_rechner(self):
        self.rechner = VonNeumannRechner(self.speichergröße, self.pio_speichergröße)
        self.rechner.pio_ausgabe = self.view.rechner_ausgabe
        self.rechner.pio_eingabe = self.view.rechner_eingabe

    def zerstöre_rechner(self):
        self.rechner = None

    def lade_programm(self, text):
        if (self.rechner!=None):
            asm = Assembler(self.rechner)
            asm.parse_text(text)
            self.rechner.lade_programm(asm.programm)
            return asm.tipps
        else:
            raise RuntimeError("Rechner muss erzeugt werden bevor Programm geladen wird")

    def lade_datei(self, datei):
        if (self.rechner!=None):
            asm = Assembler(self.rechner)
            asm.parse_datei(datei)
            self.rechner.lade_programm(asm.programm)
            return asm.tipps
        else:
            raise RuntimeError("Rechner muss erzeugt werden bevor Programm geladen wird")        

    def schritt(self):
        self.view.schritt()

    def hauptschleife(self):
        self.fertig = False
        while (not self.fertig):
            self.schritt()

    def beende(self):
        self.fertig = True

    def lade_konfiguration(self, dateiname):
        cfg = ConfigParser()
        cfg.read([dateiname])
        self.speichergröße = cfg.getint("rechner", "speichergröße")
        self.pio_speichergröße = cfg.getint("rechner", "pio_speichergröße")
        self.view.max_taktrate = cfg.getint("gui", "max_taktrate")
        self.view.setze_schriftart(cfg.get("gui", "schriftart"), cfg.getint("gui", "schriftgröße"))

if (__name__=="__main__"):
    controller = Controller()
    controller.lade_konfiguration("konfiguration.ini")
    controller.hauptschleife()
