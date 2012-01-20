
class VonNeumannRechner:
    class UnbekannterBefehl(RuntimeError):
        pass # TODO

    class Speicherzugriffsfehler(RuntimeError):
        pass # TODO
    
    def __init__(self, speichergröße = 256, pio_speichergröße = 1):
        self.speicher = [0 for i in range(speichergröße)]
        self.pio_bereich = range(speichergröße, speichergröße+pio_speichergröße)
        self.pio_eingabe = None
        self.pio_ausgabe = None
        self.register = {"SZ": speichergröße-1,
                         "SB": speichergröße-1,
                         "BZ": 0,
                         "BR": 0,
                         "AKKU": 0,
                         "ER": 0,
                         "DR": 0,
                         "AR": 0,
                         "XR": 0}
        self.befehle = {0x00: ("NOP", self.befehl_nop,  0),
                        # Transportbefehle
                        0x01: ("LDAU", self.befehl_ldau, 1),
                        0x02: ("LDAD", self.befehl_ldad, 1),
                        0x03: ("STAD", self.befehl_stad, 1),
                        0x04: ("IN",   self.befehl_in,   1),
                        0x05: ("OUT",  self.befehl_out,  1),
                        # Arithmetische Befehle
                        0x06: ("ADDU", self.befehl_addu, 1),
                        0x07: ("ADDD", self.befehl_addd, 1),
                        0x08: ("SUBU", self.befehl_subu, 1),
                        0x09: ("SUBD", self.befehl_subd, 1),
                        0x0A: ("MULU", self.befehl_mulu, 1),
                        0x0B: ("MULD", self.befehl_muld, 1),
                        0x0C: ("DIVU", self.befehl_divu, 1),
                        0x0D: ("DIVD", self.befehl_divd, 1),
                        0x0F: ("MODU", self.befehl_modu, 1),
                        0x10: ("MODD", self.befehl_modd, 1),
                        0x11: ("INC",  self.befehl_inc,  0),
                        0x12: ("DEC",  self.befehl_dec,  0),
                        # Logische Operatoren
                        0x13: ("ORU",  self.befehl_oru,  1),
                        0x14: ("ORD",  self.befehl_ord,  1),
                        0x15: ("ANDU", self.befehl_andu, 1),
                        0x16: ("ANDD", self.befehl_andd, 1),
                        0x17: ("XORU", self.befehl_xoru, 1),
                        0x18: ("XORD", self.befehl_xord, 1),
                        0x19: ("NOT",  self.befehl_not,  0),
                        0x1A: ("LSHU", self.befehl_lshu, 1),
                        0x1B: ("LSHD", self.befehl_lshd, 1),
                        0x1C: ("RSHU", self.befehl_rshu, 1),
                        0x1D: ("RSHD", self.befehl_rshd, 1),
                        # Vergleichsbefehle
                        0x1E: ("CMPU", self.befehl_cmpu, 1),
                        0x1F: ("CMPD", self.befehl_cmpd, 1),
                        # Sprungbefehle
                        0x20: ("JUM",  self.befehl_jum,  1),
                        0x21: ("JP",   self.befehl_jp,   1),
                        0x22: ("JNP",  self.befehl_jnp,  1),
                        0x23: ("JZ",   self.befehl_jz,   1),
                        0x24: ("JNZ",  self.befehl_jnz,  1),
                        0x25: ("JN",   self.befehl_jn,   1),
                        0x26: ("JNN",  self.befehl_jnn,  1),
                        0x27: ("STOP", self.befehl_stop, 0),
                        # Stapelbefehle
                        0x28: ("CAL",  self.befehl_cal,  1),
                        0x29: ("RET",  self.befehl_ret,  0),
                        0x2A: ("NEWB", self.befehl_newb, 0),
                        0x2B: ("OLDB", self.befehl_oldb, 0),
                        0x2C: ("RES",  self.befehl_res,  1),
                        0x2D: ("RED",  self.befehl_red,  1),
                        0x2E: ("PUSH", self.befehl_push, 0),
                        0x2F: ("POP",  self.befehl_pop,  0),
                        0x30: ("STL",  self.befehl_stl,  1),
                        0x31: ("LDL",  self.befehl_ldl,  1),
                        0x32: ("ADL",  self.befehl_adl,  1),
                        0x33: ("SBL",  self.befehl_sbl,  1),
                        0x34: ("STLI",  self.befehl_stl, 1),
                        0x35: ("LDLI",  self.befehl_ldl, 1),
                        0x36: ("ADLI",  self.befehl_adl, 1),
                        0x37: ("SBLI",  self.befehl_sbl, 1)}

    def lade_programm(self, programm):
        for i in range(min(len(programm), len(self.speicher))):
            self.speicher[i] = programm[i]

    def schritt(self):
        # hole befehl und parameter
        self.register["AR"] = self.register["BZ"]
        self.speicher_lesen()
        self.register["BR"] = self.register["DR"]
        if (self.register["BR"] in self.befehle):
            befehl = self.befehle[self.register["BR"]]
            parameter = []
            for i in range(befehl[2]):
                self.register["AR"] = self.register["BZ"]+1+i
                self.speicher_lesen()
                parameter.append(self.register["DR"])

            # inkrementiere befehlzeiger
            self.register["BZ"] = (self.register["BZ"]+befehl[2]+1)

            # führe befehl aus
            befehl[1](*parameter)
        else:
            raise self.UnbekannterBefehl(self.register["BZ"], self.register["BR"])

    def speicher_lesen(self):
        a = self.register["AR"]
        if (a in self.pio_bereich):
            if (self.pio_eingabe!=None):
                self.register["DR"] = self.pio_eingabe(a-self.pio_bereich[0])
        else:
            try:
                self.register["DR"] = self.speicher[a]
            except IndexError:
                raise self.Speicherzugriffsfehler(a)

    def speicher_schreiben(self):
        a = self.register["AR"]
        if (a in self.pio_bereich):
            if (self.pio_ausgabe!=None):
                self.pio_ausgabe(a-self.pio_bereich[0], self.register["DR"])
        else:
            try:
                self.speicher[a] = self.register["DR"]
            except IndexError:
                raise self.Speicherzugriffsfehler(a)

    def befehl_nop(self):
        pass

    def befehl_ldau(self, n):
        self.register["AKKU"] = n

    def befehl_ldad(self, a):
        self.register["AR"] = a
        self.speicher_lesen()
        self.register["AKKU"] = self.register["DR"]

    def befehl_stad(self, a):
        self.register["AR"] = a
        self.register["DR"] = self.register["AKKU"]
        self.speicher_schreiben()

    def befehl_in(self, p):
        self.befehl_ldad(p+self.pio_bereich[0])

    def befehl_out(self, p):
        self.befehl_stad(p+self.pio_bereich[0])

    def befehl_addu(self, n):
        self.register["AKKU"] += n

    def befehl_addd(self, a):
        self.register["AR"] = a
        self.speicher_lesen()
        self.befehl_addu(self.register["DR"])

    def befehl_subu(self, n):
        self.register["AKKU"] -= n

    def befehl_subd(self, a):
        self.register["AR"] = a
        self.speicher_lesen()
        self.befehl_subu(self.register["DR"])

    def befehl_mulu(self, n):
        self.register["AKKU"] *= n

    def befehl_muld(self, a):
        self.register["AR"] = a
        self.speicher_lesen()
        self.befehl_mulu(self.register["DR"])

    def befehl_divu(self, n):
        self.register["AKKU"] = int(self.register["AKKU"]/self.register["DR"])

    def befehl_divd(self, a):
        self.register["AR"] = a
        self.speicher_lesen()
        self.befehl_divu(self.register["DR"])

    def befehl_modu(self, n):
        self.register["AKKU"] %= n

    def befehl_modd(self, a):
        self.register["AR"] = a
        self.speicher_lesen()
        self.befehl_modu(self.register["DR"])

    def befehl_inc(self):
        self.register["AKKU"] += 1

    def befehl_dec(self):
        self.register["AKKU"] -= 1

    def befehl_oru(self, n):
        self.register["AKKU"] |= n

    def befehl_ord(self, a):
        self.register["AR"] = a
        self.speicher_lesen()
        self.befehl_oru(self, self.register["DR"])

    def befehl_andu(self, n):
        self.register["AKKU"] &= n

    def befehl_andd(self, a):
        self.register["AR"] = a
        self.speicher_lesen()
        self.befehl_andu(self, self.register["DR"])

    def befehl_xoru(self, n):
        self.register["AKKU"] ^= n

    def befehl_xord(self, a):
        self.register["AR"] = a
        self.speicher_lesen()
        self.befehl_xoru(self, self.register["DR"])

    def befehl_not(self):
        self.register["AKKU"] = not self.register["AKKU"]

    def befehl_lshu(self, n):
        self.register["AKKU"] <<= n

    def befehl_lshd(self, a):
        self.register["AR"] = a
        self.speicher_lesen()
        self.befehl_lshu(self, self.register["DR"])

    def befehl_rshu(self, n):
        self.register["AKKU"] >>= n

    def befehl_rshd(self, a):
        self.register["AR"] = a
        self.speicher_lesen()
        self.befehl_rshu(self, self.register["DR"])

    def befehl_cmpu(self, n):
        self.register["ER"] = self.register["AKKU"]-n

    def befehl_cmpd(self, a):
        self.register["AR"] = a
        self.speicher_lesen()
        self.befehl_cmpu(self, self.register["DR"])

    def befehl_jum(self, a):
        self.register["BZ"] = a

    def befehl_jp(self, a):
        if (self.register["ER"]>0):
            self.befehl_jum(a)

    def befehl_jnp(self, a):
        if (self.register["ER"]<=0):
            self.befehl_jum(a)

    def befehl_jz(self, a):
        if (self.register["ER"]==0):
            self.befehl_jum(a)

    def befehl_jnz(self, a):
        if (self.register["ER"]!=0):
            self.befehl_jum(a)

    def befehl_jn(self, a):
        if (self.register["ER"]<0):
            self.befehl_jum(a)

    def befehl_jnn(self, a):
        if (self.register["ER"]>=0):
            self.befehl_jum(a)

    def befehl_stop(self):
        # idle-schleife
        self.befehl_jum(self.register["BZ"]-1)

    def befehl_cal(self, a):
        self.register["AR"] = self.register["SZ"]
        self.register["DR"] = self.register["BZ"]
        self.speicher_schreiben()
        self.register["BZ"] = a
        self.register["SZ"] -= 1

    def befehl_ret(self):
        self.register["SZ"] += 1
        self.register["AR"] = self.register["SZ"]
        self.speicher_lesen()
        self.register["BZ"] = self.register["DR"]
        
    def befehl_newb(self):
        self.register["AR"] = self.register["SZ"]
        self.register["DR"] = self.register["SB"]
        self.speicher_schreiben()
        self.register["SB"] = self.register["SZ"]
        self.register["SZ"] -= 1

    def befehl_oldb(self):
        self.register["SZ"] += 1
        self.register["AR"] = self.register["SZ"]
        self.speicher_lesen()
        self.register["SB"] = self.register["DR"]

    def befehl_res(self, n):
        self.register["SZ"] -= n

    def befehl_red(self, n):
        self.register["SZ"] += n

    def befehl_push(self):
        self.register["AR"] = self.register["SZ"]
        self.register["DR"] = self.register["AKKU"]
        self.speicher_schreiben()
        self.register["SZ"] -= 1

    def befehl_pop(self):
        self.register["SZ"] += 1
        self.register["AR"] = self.register["SZ"]
        self.speicher_lesen()
        self.register["AKKU"] = self.register["DR"]

    def befehl_stl(self, d):
        self.register["AR"] = self.register["SB"]+d
        self.register["DR"] = self.register["AKKU"]
        self.speicher_schreiben()

    def befehl_ldl(self, d):
        self.register["AR"] = self.register["SB"]+d
        self.speicher_lesen()
        self.register["AKKU"] = self.register["DR"]

    def befehl_adl(self, d):
        self.befehl_addd(self.register["SB"]+d)

    def befehl_sbl(self, d):
        self.befehl_subd(self.register["SB"]+d)

    def befehl_stli(self, d):
        self.register["AR"] = self.register["SB"]+d
        self.speicher_lesen()
        self.register["AR"] = self.register["DR"]
        self.register["DR"] = self.register["AKKU"]
        self.speicher_schreiben()

    def befehl_ldli(self, d):
        self.register["AR"] = self.register["SB"]+d
        self.speicher_lesen()
        self.register["AR"] = self.register["DR"]
        self.speicher_lesen()
        self.register["AKKU"] = self.register["DR"]

    def befehl_adli(self, d):
        self.register["AR"] = self.register["SB"]+d
        self.speicher_lesen()
        self.befehl_addd(self.register["DR"])

    def befehl_sbli(self, d):
        self.register["AR"] = self.register["SB"]+d
        self.speicher_lesen()
        self.befehl_subd(self.register["DR"])
