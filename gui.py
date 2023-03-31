#!/usr/bin/env python3
from pynput.keyboard import Controller, Key
from keyShortcuts import *
import time
import customtkinter
import threading
import webbrowser
from PIL import Image


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.running = True
        self.thread = None

        self.geometry("500x500")
        self.title("BruteCopy   (⌐■_■)")
        self.minsize(500, 500)
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure((0,1,2,3,4), weight=1)

        self.switch_var = customtkinter.StringVar(value="off")
        self.switch = customtkinter.CTkSwitch(master=self, text="Typewriter Mode",
                                   variable=self.switch_var, onvalue="on", offvalue="off",progress_color="#3E54AC",text_color="grey")
        self.switch.grid(row=0, column=0, columnspan=5,padx=20, sticky="nsw") 

        self.logo = customtkinter.CTkImage(light_image=Image.open("logos/github-mark.png"),
                                  dark_image=Image.open("logos/github-mark-white.png"),
                                  size=(30, 30))
        
        self.helplabel1 = customtkinter.CTkLabel(master=self, text="Keyboard Shortcuts -> Go to Help",text_color="grey")
        self.helplabel1.grid(row=0, column=1, columnspan=5,padx=20, sticky="nse") 

        self.textbox = customtkinter.CTkTextbox(master=self)
        self.textbox.grid(row=1, column=0, columnspan=5, padx=20, sticky="nsew") 

        self.logobutton = customtkinter.CTkButton(master=self,image=self.logo,compound="left",width=50,command=self.callback, text="Help?",fg_color="#3E54AC")
        self.logobutton.grid(row=2, column=0, padx=20, pady=20, sticky="ew")

        self.delaylabel = customtkinter.CTkLabel(master=self, text="Delay")
        self.delaylabel.grid(row=2, column=1, padx=10, pady=20, sticky="ew")
        self.defaultvar = customtkinter.StringVar(value="5")
        self.delaybox = customtkinter.CTkComboBox(master=self,values=["1", "5","10"],variable=self.defaultvar,width=100)
        self.delaybox.grid(row=2, column=2, padx=20, pady=20, sticky="ew")

        self.cancelbutton = customtkinter.CTkButton(master=self,width=60, command=self.stop_typing, text="Cancel",state="disabled",hover_color="red",fg_color="#655DBB")
        self.cancelbutton.grid(row=2, column=3, padx=10, pady=20, sticky="ew")

        self.runbutton = customtkinter.CTkButton(master=self,width=50,command=self.start_typing, text="Run",hover_color="green",fg_color="#655DBB")
        self.runbutton.grid(row=2, column=4, padx=20, pady=20, sticky="ew")


        self.saved_text = self.textbox.get("1.0", "end-1c")
        self.shortcuts = keyShortcuts(self.saved_text)

        self.textbox.bind('<Control-Tab>',self.selected)
        self.textbox.bind("<space>", self.save_state)
        self.textbox.bind(".", self.save_state)
        self.textbox.bind("<BackSpace>", self.save_state)
        self.textbox.bind("<Control-v>", self.save_state)
        self.textbox.bind("<Return>", self.save_state)
        self.textbox.bind("<Control-z>", self.undo)
        self.textbox.bind('<Control-y>',self.redo)
        self.textbox.bind('<Control-a>', self.select_all)


    def callback(self):
        webbrowser.open_new_tab("https://github.com/slaygun")


    def type_func(self):
        keyboard = Controller()
        self.delay = int(self.delaybox.get())
        self.text = self.textbox.get("1.0","end")

        chunk_size = 0.1
        chunks = int(self.delay / chunk_size)
        for i in range(chunks):
            if not self.running:
                break
            time.sleep(chunk_size)

        for char in self.text:
            if not self.running:
                break
            if char =="\n":
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)
            else:
                keyboard.press(char)
                keyboard.release(char)
                if self.switch.get()=="on":
                    time.sleep(0.1)
            

    def start_typing(self):
        if not self.thread or not self.thread.is_alive():
            self.running = True
            self.thread = threading.Thread(target=self.type_func)

            self.runbutton.configure(state="disabled",fg_color="green")
            self.cancelbutton.configure(state="normal")

            self.thread.start()
            while self.thread and self.thread.is_alive():
                self.update()
            self.runbutton.configure(state="normal",fg_color="#655dbb")
            self.cancelbutton.configure(state="disabled",fg_color="#655dbb")
        

    def stop_typing(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
            self.thread = None
            self.cancelbutton.configure(state="disabled",fg_color="#655dbb")
    

    def save_state(self,event=None):
        current_text = self.textbox.get("1.0", "end-1c")
        self.shortcuts.savestate(current_text)


    def undo(self,event=None):
        if len(self.shortcuts.undostack)>=1:
            self.shortcuts.undo_func()
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", self.shortcuts.undoed)
        else:
            self.shortcuts.undostack.append("")
            # print("cant undo")


    def redo(self,event=None):
        if len(self.shortcuts.redostack)>1:
            self.shortcuts.redo_func()
            self.textbox.delete("1.0", "end")
            self.textbox.insert("1.0", self.shortcuts.redoed)
            return "break"
        else:
            # print("cant redo")
            return "break"
    
    
    def remove_indent(self):
        self.shortcuts.delete_indent(self.textbox.get("1.0", "end-1c"))  
        self.textbox.delete("1.0", "end")        
        self.textbox.insert("1.0", self.shortcuts.newtext)     

    def remove_indentsel(self,event=None):
        self.shortcuts.delete_indent(self.textbox.get("sel.first", "sel.last"))    
        self.textbox.delete("sel.first", "sel.last")  
        self.textbox.insert("insert", self.shortcuts.newtext)

    def selected(self,event=None):
        textbox=self.textbox
        selected_text = textbox.tag_ranges("sel")
        if selected_text:
            self.remove_indentsel()
        else:
            self.remove_indent()
        return "break"

    def select_all(self,event=None):
        self.textbox.tag_add('sel', '1.0', 'end')
        return "break"
    
if __name__ == "__main__":
    app = App()
    app.textbox
    app.mainloop()


    