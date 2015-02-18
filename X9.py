# -*- coding: cp1252 -*-


##    This file is part of X9.
##
##    Foobar is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    Foobar is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
##	
##    Autor: Carlos Lima
##    Email: lima.carlosr@gmail.com

import ctypes
import string
import json
import socket
import requests
import urllib
import urllib2
from threading import Timer
from Tkinter import *

##root = Tk() # alias lib Tkinter
##root.wm_title("X9") # alter title bar
##root.geometry('1024x200-400+40')
##
##frame = Frame(root,relief=RIDGE)
##frame=Frame(root,width=1024,height=200)
##frame.grid(row=0,column=0)
##
##canvas=Canvas(frame,bg='#FFFFFF',width=1024,height=400,scrollregion=(0,0,500,500))
##canvas.pack()
###hbar=Scrollbar(frame,orient=HORIZONTAL)
###hbar.pack(side=BOTTOM,fill=X)
###hbar.config(command=canvas.xview)
##vbar=Scrollbar(frame,orient=VERTICAL)
##vbar.pack(side=RIGHT,fill=Y)
##vbar.config(command=canvas.yview)
##canvas.config(width=1024,height=400)
###canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
##canvas.config(yscrollcommand=vbar.set)

valueInputUser = "" #name of input user
rt = ""

class App(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        master.wm_title("X9")
        master.wm_iconbitmap(bitmap = "x9.ico")
        master.resizable(width=FALSE, height=FALSE)
        screen_w = 1024
        screen_h = 300
        #master.minsize(width=screen_w, height=screen_h)
        #master.maxsize(width=screen_w, height=screen_h)
        menubar = Menu(master)
        menubar.add_command(label="Atualizar", command= lambda: self.refreshWindow(master))

        master.config(menu=menubar)
        
        #declare vars list windows
        self.EnumWindows = ctypes.windll.user32.EnumWindows
        self.EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        self.GetWindowText = ctypes.windll.user32.GetWindowTextW
        self.GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        self.IsWindowVisible = ctypes.windll.user32.IsWindowVisible

        #declare vars local program
        self.titles = []

        self.COMPUTER_NAME = socket.gethostname()

        self.gridValues = {}
        
        #start and refresh window
        self.refreshWindow(master)
        
        global rt        
        rt = RepeatedTimer(10, self.refreshBg)

    def syncWindow(self,data):
        json_encoded = json.dumps(data)

        #create arguments for request
        query_args = { 'json':json_encoded }
        encoded_args = urllib.urlencode(query_args)
        #send data
        response = urllib2.urlopen('http://quartetoapp.com/receive.php/?' + encoded_args)
        #receive data / load
        responseLoadX9 = urllib2.urlopen('http://quartetoapp.com/load_x9.php')
        #read data with window names of users
        dataReturn = responseLoadX9.read()

        return dataReturn

    def refreshBg(self):
        self.titles = []
        self.gridValues = {}

        self.EnumWindows(self.EnumWindowsProc(self.foreach_window), 0)

        #create json
        dataRefresh = {'sender': self.COMPUTER_NAME
                     , 'window': self.titles}

        print dataRefresh

        #send and get data
        dataRefresh = self.syncWindow(dataRefresh)

    def enterUserCall(self,event):
        d = MyDialog(self)
        root.wait_window(d.top)
        global valueInputUser
        global rt
        rt.start() ##start refresh sync
        
        #create json
        if valueInputUser <> '':
            dataUser = {'user': valueInputUser
                      , 'sender': self.COMPUTER_NAME
                      , 'PID': self.gridValues[ event.widget ]}

            json_encoded_user = json.dumps(dataUser)

            print json_encoded_user

            #create arguments for request
            query_args = { 'json':json_encoded_user }
            encoded_args = urllib.urlencode(query_args)
            #send data
            response = urllib2.urlopen('http://quartetoapp.com/receive_user.php/?' + encoded_args)
            self.refreshWindow(root)

    #search windows open
    def foreach_window(self, hwnd, lParam):

        if self.IsWindowVisible(hwnd):
            length = self.GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            self.GetWindowText(hwnd, buff, length + 1)
            #search conection remote
            w_dados_lower = buff.value
            w_dados_lower = w_dados_lower.lower()
            word_find = string.find(w_dados_lower,"trabalho remota")
            processID = ctypes.c_int()
            threadID = ctypes.windll.user32.GetWindowThreadProcessId(hwnd,ctypes.byref(processID))
            
            if word_find != -1:
                titlesValues = {}
                titlesValues["name"] = buff.value
                titlesValues["PID"] = threadID
                self.titles.append(titlesValues) #save window name
              
        return True

    def destroy_grid(self,master):
        self.destroy()        
        Frame.__init__(self, master)
        self.grid()

    def refreshWindow(self,master):

        self.destroy_grid(master)
        
        global titles
        global gridValues
        global canvas
        
        self.titles = []
        self.gridValues = {}

        self.EnumWindows(self.EnumWindowsProc(self.foreach_window), 0)

        #create json
        dataRefresh = {'sender': self.COMPUTER_NAME
                     , 'window': self.titles}

        print dataRefresh

        #send and get data
        dataRefresh = self.syncWindow(dataRefresh)

        print dataRefresh

        if len(dataRefresh) == 0:
            self.lx = Label(self,text="Nenhuma janela ativa no momento!", relief=RIDGE,width=60)
            self.lx.grid(row=0,column=0)

        if len(dataRefresh) > 0:

            dataJson = json.loads(dataRefresh)
        
            array_local_data = []

            idGrid = 0
        
            for json_data in dataJson['data']:
                array_local_data.append([json_data['PID']
                                        ,json_data['name']
                                        ,json_data['window']
                                        ,json_data['user']])        

            for i in range(len(array_local_data)):
                for j in range(5):
                    local_user = array_local_data[i][1]
                    wts_user   = array_local_data[i][3]
                    line_color = ""
                    
                    if wts_user == "?":
                        line_color = "yellow"
                    else:
                        line_color = "snow"
                        
                    if j == 0:
                        self.l0 = Label(self,text=array_local_data[i][j], relief=RIDGE,width=5, bg=line_color)
                        self.l0.grid(row=i,column=j)
                        idGrid = array_local_data[i][j]
                        
                    if j == 1:
                        self.l1 = Label(self,text=array_local_data[i][j], relief=RIDGE,width=40, bg=line_color)
                        self.l1.grid(row=i,column=j)
                        
                    if j == 2:
                        self.l2 = Label(self,text=array_local_data[i][j], relief=RIDGE,width=60, bg=line_color)
                        self.l2.grid(row=i,column=j)
                    if j == 3:
                        self.l3 = Label(self,text=array_local_data[i][j], relief=RIDGE,width=20, bg=line_color)
                        self.l3.grid(row=i,column=j)
                    if j == 4:
                        if local_user == self.COMPUTER_NAME:
                            self.b = Button(self,text ="DIGITAR USUÁRIO", bg="white",fg="blue")
                            self.b.bind("<Button-1>", self.enterUserCall)
                        else:
                            self.b = Button(self,text ="DIGITAR USUÁRIO", bg="white",fg="blue",state=DISABLED)
                        self.b.grid(column=j, row=i)
                        self.gridValues[ self.b ] = idGrid
                        
            

            
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

class MyDialog:
    def __init__(self, parent):

        top = self.top = Toplevel(parent)

        border = top.winfo_rootx() - top.winfo_x()

        titlebar_height = top.winfo_rooty() - top.winfo_y()

        win_width = top.winfo_width() + (border * 2)
        win_height = top.winfo_height() + titlebar_height + border
         
        x = (root.winfo_screenwidth() - win_width) / 2 - 200
        y = (root.winfo_screenheight() - win_height) / 2 - 100
 
        top.geometry( '{0}x{1}+{2}+{3}'.format( 200, 50, x, y))

        Label(top, text="Digite o usuário:").pack()

        self.e = Entry(top,justify="center",bd =5,width=30)
        self.e.pack(side=LEFT)
        self.e.focus()

        #b = Button(top, text="OK", command=self.ok)
        #b.pack(pady=5)
        global rt
        rt.stop()

        top.bind('<Return>', self.ok)

    def ok(self,event):

        global valueInputUser
        valueInputUser = self.e.get()
        self.top.destroy()
                    
               
#canvas.pack(side=LEFT,expand=True,fill=BOTH)

root = Tk()
app = App(master=root)
app.mainloop()


