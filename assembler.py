
class Assembler:
    def __init__(self, rechner):
        self.befehle = {}
        for num in rechner.befehle:
            befehl = rechner.befehle[num]
            self.befehle[befehl[0]] = (num, befehl[2])
        self.bz = 0
        self.momentanes_label = ""
        self.labels = {}
        self.programm = []
        self.tipps = {}

    def parse_label(self, label):
        label = label.strip()
        if (label[0]=="."):
            return self.momentanes_label+label
        else:
            return label

    def parse_ausdruck(self, ausdruck, zeilennummer = "unbekannt"):
        if (ausdruck.isnumeric()):
            return int(ausdruck)
        else:
            label = self.parse_label(ausdruck)
            if (label in self.labels):
                return self.labels[label]
        raise SyntaxError("Weder Label noch Zahl '"+str(ausdruck)+"' in Zeile "+str(zeilennummer)+".")

    def parse_zeile(self, zeile, zeilennummer = "unbekannt", erzeuge_tipps = False, nur_labels = False):
        # entferne kommentare
        zeile = zeile.split("#", 2)[0]
        zeile = zeile.split(";", 2)[0]

        if (not zeile.isspace() and zeile!=""):
            if (erzeuge_tipps):
                # merke assembler-befehl
                if (self.bz not in self.tipps):
                    self.tipps[self.bz] = zeile.strip()
                else:
                    self.tipps[self.bz] += " "+zeile.strip()

            # parse label-befehl-paare
            lb = zeile.split(":", 2)
            if (len(lb)==1):
                befehl = lb[0]
            elif (len(lb)==2):
                label = self.parse_label(lb[0])
                self.labels[label] = self.bz
                if (lb[0].strip()[0]!='.'):
                    self.momentanes_label = label
                befehl = lb[1]

            # parse befehl
            if (not befehl.isspace() and befehl!=""):
                befehl = list(map(lambda b: b.strip(), befehl.split()))
                befehl[0] = befehl[0].upper()
                if (befehl[0]=="SB"):
                    # psuedo-befehl zum setzen von Bytes
                    bytes = befehl[1:]
                    for b in bytes:
                        if (not nur_labels):
                            self.programm.append(self.parse_ausdruck(b, zeilennummer))
                        self.bz += 1
                elif (befehl[0] in self.befehle):
                    if (len(befehl)-1!=self.befehle[befehl[0]][1]):
                        raise SyntaxError("Befehl '"+befehl[0]+"' erwartet "+str(self.befehle[befehl[0]][1])+" Parameter ("+str(len(befehl)-1)+" gegeben) in Zeile "+str(zeilennummer)+".")
                    if (not nur_labels):
                        self.programm.append(self.befehle[befehl[0]][0])
                    self.bz += 1
                    for i in range(1, len(befehl)):
                        if (not nur_labels):
                            self.programm.append(self.parse_ausdruck(befehl[i], zeilennummer))
                        self.bz += 1
                else:
                    raise SyntaxError("Unbekannter befehl '"+befehl[0]+"' in Zeile "+str(zeilennummer)+".")

    def parse_datei(self, datei):
        if (type(datei)==str):
            datei = open(datei)
        self.parse_zeilen(datei.readlines())

    def parse_text(self, text):
        self.parse_zeilen(text.split('\n'))

    def parse_zeilen(self, zeilen):
        # parse Labels
        i = 1
        for zeile in zeilen:
            self.parse_zeile(zeile, i, False, True)
            i += 1

        # parse Code
        self.bz = 0
        i = 1
        for zeile in zeilen:
            self.parse_zeile(zeile, i, True)
            i += 1
