import tkinter as tk

class SyntaxText(tk.Text):
    def __init__(self, root, **options):
        schriftart = options.pop("schriftart", "helvetica")
        schriftgröße = options.pop("schriftgröße", 10)
        self.befehle = options.pop("befehle", [])
        tk.Text.__init__(self, root, **options)
        self.setze_schriftart(schriftart, schriftgröße)
        self.bind('<KeyRelease>', self.key_press)

    def setze_schriftart(self, art, größe):
        self.schriftart = art
        self.schriftgröße = größe
        self.config(font = art+" "+str(größe))
        self.config_tags()

    def config_tags(self):
        self.tags = {"befehl":   {"foreground": "#000000",
                                 "font": self.schriftart+" "+str(self.schriftgröße)+" bold"},
                    "kommentar": {"foreground": "#808080",
                                  "font": self.schriftart+" "+str(self.schriftgröße)+" italic"},
                    "label":     {"foreground": "#000080"},
                    "zahl":      {"foreground": "#0000FF"},
                    "rohdaten":  {"foreground": "#800000"}}
        for tag in self.tags:
            self.tag_config(tag, **self.tags[tag])

    def remove_tags(self, start, end):
        for tag in self.tags.keys():
            self.tag_remove(tag, start, end)

    def key_press(self, key):
        self.changed()

    def delete(self, index1, index2 = None):
        self.remove_tags(index1, index2)
        tk.Text.delete(self, index1, index2)

    def insert(self, index, text, tags = None):
        tk.Text.insert(self, index, text, tags)
        num_lines = len(text.splitlines())
        line = int(index.split(".")[0])
        for i in range(line, line+num_lines):
            self.changed(i)

    def changed(self, cline = None):
        if (cline==None):
            cline = self.index("insert").split('.')[0]
        lastcol = 0
        char = self.get('%s.%d'%(cline, lastcol))
        while char != '\n':
            lastcol += 1
            char = self.get('%s.%d'%(cline, lastcol))
        lastcol += 1
        buffer = self.get('%s.%d'%(cline,0),'%s.%d'%(cline,lastcol))

        self.remove_tags('%s.%d'%(cline, 0), '%s.%d'%(cline, lastcol))

        k1 = buffer.find(';')
        k2 = buffer.find('#')
        if (k1==-1 or k2==-1):
            kommentar = max(k1, k2)
        else:
            kommentar = min(k1, k2)
        if (kommentar!=-1):
            self.tag_add('kommentar', '%s.%d'%(cline, kommentar), '%s.%d'%(cline, lastcol))
            buffer = buffer[:kommentar]

        tokenized = buffer.split(' ')
        start, end = 0, 0
        for token in tokenized:
            end = start + len(token)
            if token.strip().upper() in self.befehle:
                self.tag_add('befehl', '%s.%d'%(cline, start), '%s.%d'%(cline, end))
            elif (token.isnumeric()):
                self.tag_add('zahl', '%s.%d'%(cline, start), '%s.%d'%(cline, end))
            elif (token.endswith(':')):
                self.tag_add('label', '%s.%d'%(cline, start), '%s.%d'%(cline, end))
            start += len(token)+1
 
