class keyShortcuts:
    def __init__(self,savedtext):
        self.savedstack = []
        self.savedstack.append(savedtext)
        self.undostack = []
        self.undostack.append(savedtext)
        self.redostack = []
        
    def savestate(self,currenttext):
        if currenttext != self.savedstack[-1]:
            self.savedtext = currenttext
            self.savedstack.append(self.savedtext)
            self.undostack.append(self.savedtext) 

    def delete_indent(self,text):
        self.lines = text.split("\n")          
        self.newlines = [line.lstrip() for line in self.lines]  
        self.newtext = "\n".join(self.newlines)

    def undo_func(self):
        self.popundo=self.undostack[-1]
        self.undostack.pop(-1)
        self.redostack.append(self.popundo)
        self.undoed=self.undostack[-1]

    def redo_func(self):
        self.popredo=self.redostack[-1]
        self.redostack.pop(-1)
        self.undostack.append(self.popredo)
        self.redoed=self.redostack[-1]

