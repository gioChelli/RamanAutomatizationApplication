import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, ttk, messagebox
import mysql.connector
import os.path
import threading
import asyncio
import websockets
import requests
from queue import Empty
import time
import io
import queue
import json
from PIL import Image, ImageTk
from .match_pattern import match_pattern
from .slide_analisys import slide_analisys
import zipfile
import shutil

Image.MAX_IMAGE_PIXELS = None #serve per disattivare limite di sicurezza per grandezza immagini di PIL
MICRONx_x5 = 960
MICRONy_x5 = 810
PIXEL_IMG_x = 428
PIXEL_IMG_y = 360

# Connessione al database locale
conn = mysql.connector.connect(
    host="localhost",      
    user="root",
    password="Giocondo2021$",
    autocommit = True
)

class ctkinter:
    def __init__(self):

        self.cursor = conn.cursor(dictionary=True)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        #self.cursor.execute("DROP DATABASE IF EXISTS Raman_DB")
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS Raman_DB")
        self.cursor.execute("USE Raman_DB")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Slide(
        Filepath VARCHAR(255) PRIMARY KEY,
        NanoGPS BOOLEAN NOT NULL DEFAULT False,
        x_nano FLOAT,
        y_nano FLOAT,
        ContourPath TEXT
        )""")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Pattern(
            ID INT PRIMARY KEY AUTO_INCREMENT,
            Slide VARCHAR(255) NOT NULL,
            x_min FLOAT,
            y_min FLOAT,
            x_max FLOAT,
            y_max FLOAT,
            x_centr FLOAT,
            y_centr FLOAT,
            Colored BOOLEAN NOT NULL,
            x10 BOOLEAN NOT NULL DEFAULT FALSE,
            images_tree JSON,                             
            FOREIGN KEY (Slide) REFERENCES Slide(Filepath) ON DELETE CASCADE
            )
        """)

        #controllo se sono stati eliminati alcuni vetrini, in caso positivo li elimino anche dal DB
        query = self.cursor.execute("SELECT * FROM Slide")
        result = self.cursor.fetchall()
            
        if result:
            for tex in result:
                path = os.path.join(os.getcwd(), tex["Filepath"])
                if not os.path.exists(path):
                    self.cursor.execute("DELETE FROM Slide WHERE Filepath = %s", (tex["Filepath"],))
                    conn.commit()

        #creazione della directory in cui salvare i vetrini analizzati
        
        dirSample = os.path.join("tessuti")
        if not os.path.exists(dirSample):
            os.makedirs(dirSample)

        self.ctk = ctk.CTk()
        self.ctk.geometry("800x800")
        self.ctk.title("RamanApp")
        self.ctk.iconbitmap("RamanApplicationIcon.ico")
        self.ctk.grid_rowconfigure(0, weight=1)
        self.ctk.grid_columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self.ctk)
        self.notebook.pack(expand=True, fill='both')
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.frame1 = ctk.CTkFrame(self.notebook)
        self.frame2 = ctk.CTkFrame(self.notebook)
        self.frame3 = ctk.CTkFrame(self.notebook)
        #self.frame4 = ctk.CTkFrame(self.notebook)

        self.frame1.grid_rowconfigure(0, weight=1)
        self.frame1.grid_columnconfigure(0, weight=1)

        self.frame2.grid_rowconfigure(0, weight=1)
        self.frame2.grid_columnconfigure(0, weight=1)
        
        self.frame3.grid_rowconfigure(0, weight=1)
        self.frame3.grid_columnconfigure(0, weight=1)

        #self.frame4.grid_rowconfigure(0, weight=1)
        #self.frame4.grid_columnconfigure(0, weight=1)

        self.notebook.add(self.frame1, text="Visualizzazione vetrini")
        self.notebook.add(self.frame2, text="Matching")
        self.notebook.add(self.frame3, text="Acquisizione Raman")
        #self.notebook.add(self.frame4, text="Visualizzazione Spettri")
        self.notebook.tab(self.frame3, state="disabled")

        self.scroll1 = ctk.CTkScrollableFrame(self.frame1)
        self.scroll1.grid(row=0, column=0, sticky="nsew")

        self.scroll2 = ctk.CTkScrollableFrame(self.frame2)
        self.scroll2.grid(row=0, column=0, sticky="nsew")

        self.scroll3 = ctk.CTkScrollableFrame(self.frame3)
        self.scroll3.grid(row=0, column=0, sticky="nsew")

        #self.scroll4 = ctk.CTkScrollableFrame(self.frame4)
        #self.scroll4.grid(row=0, column=0, sticky="nsew")

        self.scroll1.grid_columnconfigure(0, weight=1)
        self.scroll1.grid_columnconfigure(1, weight=1)
        self.scroll1.grid_columnconfigure(2, weight=1)
        self.scroll1.grid_columnconfigure(3, weight=1)

        self.scroll2.grid_columnconfigure(0, weight=1)
        self.scroll2.grid_columnconfigure(1, weight=1)
        self.scroll2.grid_columnconfigure(2, weight=1)

        self.scroll3.grid_columnconfigure(0, weight=1)
        self.scroll3.grid_columnconfigure(1, weight=1)

        #self.scroll4.grid_columnconfigure(0, weight=1)
        #self.scroll4.grid_columnconfigure(1, weight=1)

        self.lock = threading.Lock()

        #button del software
        self.analisys = None
        self.acquire = None
        self.matchButton = None
        self.coloredButton = None
        self.naturalButton = None
        self.matchSlide = None
        self.ramanAcquisition = None
        self.highResolution = None

        self.img1 = None
        self.img2 = None
        self.info = None
        self.labelAnalyxed = None
        self.saveImg1 = None
        self.saveImg2 = None
        self.scelta1 = ctk.StringVar()
        self.scelta2 = ctk.StringVar()
        self.scelta1.set("A")
        self.scelta2.set("B")
        
        ctk.CTkLabel(self.scroll1, text="Visualizzazione vetrino", font=("Helvetica", 40), anchor="center", text_color="blue").grid(row=0, columnspan=4, pady = 8)
        ctk.CTkLabel(self.scroll1, text="Carica un campione da disco oppure inizia un acquisizione con il microspettrometro LabSpec6").grid(row=1, columnspan=4, pady=4)
        self.connectedSignal = ctk.CTkLabel(self.scroll1, text="", width=20, height=1, fg_color="red")
        self.connectedSignal.grid(row=2, column=0, columnspan=2, sticky='e', padx=20)
        self.connected = ctk.CTkLabel(self.scroll1, text="Spettrometro disconnesso")
        self.connected.grid(row=2, column=2, columnspan=2, pady=3, sticky='w')
        ctk.CTkButton(self.scroll1, text="Carica", command=lambda:self.open_file()).grid(row=3, column = 0, columnspan=2,  padx = 15, pady = 8, sticky='e')
        self.acquire = ctk.CTkButton(self.scroll1,  command=lambda:self.startAcquisition(), text="Acquisisci")
        self.acquire.grid(row=3, column = 2, columnspan=2, padx = 15, pady = 8, sticky='w')
        self.acquire.configure(state="disabled")

        ctk.CTkLabel(self.scroll2, text="Matching campioni", font=("Helvetica", 40), text_color="blue").grid(row=1, columnspan=3, pady = 10)
        self.coloredButton = ctk.CTkButton(self.scroll2, text="Scegli campione colorato", command=lambda:self.open_file_preview(1))
        self.coloredButton.grid(row=2, column = 0, pady = 50)
        self.label1 = ctk.CTkLabel(self.scroll2, text="Nessun Path selezionato al momento", anchor='w')
        self.label1.grid(row=2, column=1, sticky='w')
        ctk.CTkLabel(self.scroll2, text="").grid(row=3, pady=2)
        self.naturalButton = ctk.CTkButton(self.scroll2, text="Scegli campione naturale", command=lambda:self.open_file_preview(2))
        self.naturalButton.grid(row=4, column = 0, pady =50)
        self.label2 = ctk.CTkLabel(self.scroll2, text="Nessun Path selezionato al momento", anchor='w')
        self.label2.grid(row=4, column=1, sticky='w')

        self.label_chooseL = ctk.CTkLabel(self.scroll2, text="Scegli un campione del primo vetrino:")
        self.label_chooseL.grid(row=5,column=0)
        self.label_chooseL1 = ctk.CTkRadioButton(self.scroll2, text="Campione sinistro", variable=self.scelta1, value="A")
        self.label_chooseL1.grid(row=5, column=1)
        self.label_chooseL2 = ctk.CTkRadioButton(self.scroll2, text="Campione destro", variable=self.scelta1, value="B")
        self.label_chooseL2.grid(row=5, column=2)
        self.label_chooseR = ctk.CTkLabel(self.scroll2, text="Scegli un campione del secondo vetrino:")
        self.label_chooseR.grid(row=6,column=0)
        self.label_chooseR1 = ctk.CTkRadioButton(self.scroll2, text="Campione sinistro", variable=self.scelta2, value="A")
        self.label_chooseR1.grid(row=6, column=1)
        self.label_chooseR2 = ctk.CTkRadioButton(self.scroll2, text="Campione destro", variable=self.scelta2, value="B")
        self.label_chooseR2.grid(row=6, column=2)

        #ctk.CTkLabel(self.scroll4, text="Visualizzazione spettri", font=("Helvetica", 40), text_color="blue").grid(row=1, pady = 10)
        #ctk.CTkButton(self.scroll4, text="Carica", command=lambda:self.open_spectrum()).grid(row=2, column = 0, padx = 15, pady = 8)

        self.message_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.startConnection)
        self.thread.start()

        self.ctk.protocol("WM_DELETE_WINDOW", self.on_close)
    
    #per gestire lo scorrere con la rotella
    def on_tab_change(self, event):
        tab = event.widget.tab(event.widget.select(), "text")
        if tab == "Visualizzazione":
            self.scroll1._parent_canvas.focus_set()
        elif tab == "Matching":
            self.scroll2._parent_canvas.focus_set()
        elif tab == "Acquisizione Raman":
            self.scroll3._parent_canvas.focus_set()

    def stop_loop(self,loop):
        # Recupera tutti i task ancora attivi
        tasks = [t for t in asyncio.all_tasks(loop) if not t.done()]

        for task in tasks:
            task.cancel()  # cancella il task

        async def shutdown():
            await asyncio.gather(*tasks, return_exceptions=True)

        fut = asyncio.run_coroutine_threadsafe(shutdown(), loop)

        def stop_loop_when_done(_):
            loop.stop()

        fut.add_done_callback(stop_loop_when_done)

    #gestione della chiusura della finestra
    def on_close(self,event=None):
        
        conn.close()
        self.stop_event.set()
        if self.loop and self.loop.is_running():
            self.stop_loop(self.loop)
        print("in chiusura")
        self.thread.join()
        print("non ce la fa")
        self.ctk.destroy()

    #avvio funzione per la connessione con il microscopio LabSpec
    def startConnection(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.requireConnection())
        except asyncio.CancelledError:
            print("Coroutine cancelled")
        except RuntimeError as e:
            print(f"RuntimeError nel loop: {e}")
        finally:
            self.loop.close()

    #gestione connessione col microscopio
    async def requireConnection(self):
        self.connAval = False
        operation = False
        acquisition = False
        last_raman_path = None
        uri = "ws://127.0.0.1:5500/stateWs"
        x = []
        y = []
        try:
            while not self.stop_event.is_set():
                try:
                    async with websockets.connect(uri, max_size = None,ping_interval=60, ping_timeout=30) as websocket:
                        while not self.stop_event.is_set():
                            try:
                                print(operation)
                                if self.connAval and not operation:
                                    try:
                                        op = self.message_queue.get_nowait()
                                        print(op)
                                        if op is not None:
                                            operation = True
                                            await websocket.send(json.dumps(op))
                                            if op["request"] == "patternAcquisition":
                                                folder = str(op["min_x"]) + "_" + str(op["min_y"])
                                                highResolution = False
                                            elif op["request"] == "ramanAcquisition":
                                                x.append(op["ramanX"])
                                                y.append(op["ramanY"])   
                                            elif op["request"] == "acquisition":
                                                acquisition = False    
                                    except Empty:
                                        self.ctk.after(0, self.updateLabSpecState, "Spettrometro connesso", "green", 'normal')
                                #if self.connAval and operation:
                                #    op = self.message_queue.get_nowait()
                                #    if op is not None and op["request"] == "stopAcquisition":
                                #        print("stop")
                                #        await websocket.send(json.dumps(op))
                                #    else:
                                #        self.message_queue.put(op)
                                #        reqConnection = {"request":"RequireLabSpec6Connection"}
                                #    print("Richiesto", reqConnection)
                                #    await websocket.send(json.dumps(reqConnection))
                                elif (self.connAval and operation) or not self.connAval:
                                    reqConnection = {"request":"RequireLabSpec6Connection"}
                                    print("Richiesto", reqConnection)
                                    await websocket.send(json.dumps(reqConnection))
                                try:
                                    if operation or not self.connAval:
                                        print("in attesa")
                                        msgJson = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                                        message = json.loads(msgJson)
                                        print("Ricevuto:", message)
                                except asyncio.TimeoutError:
                                    print("riprovo")
                                    continue
                                except websockets.exceptions.ConnectionClosed:
                                    print("disconnesso")
                                    self.ctk.after(0, self.updateLabSpecState, "Spettrometro disconnesso", "red", 'disabled')
                                    self.connAval = False
                                    operation = False
                                    break 
                                if message["state"] == "connected":
                                    if not operation:
                                        self.ctk.after(0, self.updateLabSpecState, "Spettrometro connesso", "green", 'normal')
                                        self.connAval = True
                                elif message["state"] == "stopped":
                                    self.ctk.after(0, self.updateLabSpecState, "Spettrometro connesso", "green", 'normal')
                                elif message["state"] == "disconnected":
                                    self.ctk.after(0, self.updateLabSpecState, "Spettrometro disconnesso", "red", 'disabled')
                                    self.connAval = False
                                    operation = False
                                elif message["state"] == "error":
                                    self.ctk.after(0, self.updateLabSpecState, "Errore nell'acquisizione", "green", 'normal')
                                    self.connAval = False
                                    operation = False
                                elif message["state"] == "started":
                                    self.ctk.after(0, self.updateLabSpecState, "Acquisizione in corso", "orange", 'disabled')
                                #elif message["state"] == "startedAcquisition":
                                #    self.ctk.after(0, self.updateLabSpecState, "Acquisizione in corso", "orange", 'disabled')
                                #    self.ctk.after(0, self.updateAcquisition, "Annulla") 
                                elif message["state"] == "done" and message["operation"] == "acquisition" and not acquisition:
                                    operation = False
                                    acquisition = True
                                    imagePath = message["path"]
                                    timestamp = int(time.time())
                                    url = f"http://localhost:5500/image/{imagePath}?timestamp=={timestamp}"
                                    r = requests.get(url)
        
                                    if r.status_code == 200:
                                        try:
                                            img = Image.open(io.BytesIO(r.content))
                                            self.ctk.after(0, self.save_image, img)
                                            self.ctk.after(0, self.updateLabSpecState, "Spettrometro connesso", "green", 'normal')
                                        except Exception as e:
                                            self.ctk.after(0, self.updateLabSpecState, "Errore nell'acquisizione", "green", 'normal')
                                    else:
                                        self.ctk.after(0, self.updateLabSpecState, "Spettrometro connesso", "green", 'normal')
                                elif message["state"] == "done" and message["operation"] == "ramanAcquisition":
                                    
                                    ramanPath = message["path"]
                                    if ramanPath == last_raman_path:
                                        continue  # già gestito
                                    last_raman_path = ramanPath
                                    self.highResolution.configure(state='normal')
                                    ramanPath = message["path"]
                                    timestamp = int(time.time())
                                    url = f"http://localhost:5500/raman/{ramanPath}?timestamp={timestamp}"
                                    r = requests.get(url)
                                    operation = False
                                    
                                    if r.status_code == 200:
                                        with self.lock:
                                            dirname = os.path.dirname(self.filepath_var2.get())
                                        
                                        dir = os.path.join(dirname, "Raman_Acquisition") 
                                        os.makedirs(dir, exist_ok=True)
                                        filename = os.path.join(dir, f"{str(x.pop(0))}_{str(y.pop(0))}.txt")
                                        with open(filename, "w", encoding="utf-8") as f:
                                            f.write(r.text)
                                        
                                    else:
                                        self.ctk.after(0, self.updateLabSpecState, "Errore nell'acquisizione", "red", 'disabled')
                                elif message["state"] == "done" and message["operation"] == "patternAcquisition" and not highResolution:
                                    operation = False
                                    highResolution = True
                                    timestamp = int(time.time())
                                    url = f"http://localhost:5500/highResolutionImages?timestamp={timestamp}"
                                    r = requests.get(url)

                                    if r.status_code == 200:

                                        with zipfile.ZipFile(io.BytesIO(r.content)) as zip_ref:
                                            with self.lock:
                                                dirname = os.path.dirname(self.filepath_var1.get())
                                                extract_dir = os.path.join(dirname, folder) 
                                                
                                                if os.path.exists(extract_dir):
                                                    shutil.rmtree(extract_dir)
                                                os.makedirs(extract_dir)
                                                zip_ref.extractall(extract_dir)
                                                for file_name in zip_ref.namelist():
                                                    full_path = os.path.join(extract_dir, file_name)
                                                    self.treeJson[folder]["child"].append({
                                                        "path": full_path,
                                                        "child": []
                                                    })
                                                new_json = json.dumps(self.treeJson)
                                                #aggiorna db
                                                cursor = conn.cursor(dictionary=True)
                                                cursor.execute("""UPDATE Pattern SET images_tree = %s WHERE ID = %s""", (new_json, self.pattIdx))
                                                conn.commit()
                                                cursor.close()

                                        if self.message_queue.empty():
                                            self.ctk.after(0, self.createResImage)
                                            self.ctk.after(0, self.updateLabSpecState, "Spettrometro connesso", "green", 'normal')
                                    else:
                                        self.ctk.after(0, self.updateLabSpecState, "Errore nell'acquisizione", "green", 'normal')

                                for _ in range(100):  # 5 sec in 100ms step
                                    if self.stop_event.is_set():
                                        return
                                    await asyncio.sleep(0.1)
                            except asyncio.TimeoutError:
                                pass
                except Exception as e:
                    self.ctk.after(0, self.updateLabSpecState, "Spettrometro disconnesso", "red", 'disabled')
                    for _ in range(30):  # 5 sec in 100ms step
                        if self.stop_event.is_set():
                            return
                    await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            print("requireConnection: coroutine cancellata")
    
    """ #per stoppare acquisizione
    def stopAcquisition(self):
        req = {"request":"stopAcquisition"}
        self.message_queue.put(req)
        with self.lock:
            self.acquire.configure(command=lambda:self.startAcquisition(), text="Acquisisci")

    def updateAcquisition(self, txt):
        self.acquire.configure(text=txt, command=lambda:self.stopAcquisition())
        self.acquire.configure(state='normal') """

    #aggiornamento dell'interfaccia relativa allo stato della connessione
    def updateLabSpecState(self, text, color, state):
        self.acquire.configure(state=state, command=lambda:self.startAcquisition(), text="Acquisisci")
        self.connectedSignal.configure(fg_color=color) 
        self.connected.configure(text=text)
        if hasattr(self, 'connectedSignal2'):
            self.connectedSignal2.configure(fg_color=color) 
            self.connected2.configure(text=text)
        if hasattr(self, 'ramanAcquisition') and self.ramanAcquisition is not None:
            self.ramanAcquisition.configure(state=state)

    #FUNZIONI CHE POSSONO ESSERE ATTIVATE NEL PRIMO NOTEBOOK

    #funzione per la selezione del vetrino da visualizzare
    def open_file(self):
        dirSample = os.path.join(os.getcwd(), "tessuti")
        self.filepath = filedialog.askopenfilename(initialdir=dirSample)  # Apri la finestra di dialogo per selezionare un file

        if self.filepath and os.path.commonpath([dirSample, self.filepath]) == dirSample:    

            if self.info is not None:
                self.info.grid_remove()
            try:
                img = Image.open(self.filepath)
                img.thumbnail((1000, 1000))  # Riduce mantenendo le proporzioni
            except Exception:
                if self.labelAnalyxed is not None:
                    self.labelAnalyxed.grid_remove()
                self.labelAnalyxed = ctk.CTkLabel(self.scroll1, text="File non valido")
                self.labelAnalyxed.grid(row=4, column=0, columnspan=4)
                return -1
            
            photo = ctk.CTkImage(light_image=img, size=(800, 400))
            label = ctk.CTkLabel(self.scroll1, image=photo, text="")
            label.grid(row=4, columnspan = 4, padx=3)
            label.image = photo
            #self.img1 = img

            actual_row = 5
            relative_path = os.path.relpath(self.filepath,  os.getcwd()) 
            self.cursor.execute("SELECT * FROM Slide WHERE Filepath = %s", (relative_path,))
            result = self.cursor.fetchall()
            
            if result:
                if self.labelAnalyxed is not None:
                    self.labelAnalyxed.grid_remove()
                self.labelAnalyxed = ctk.CTkLabel(self.scroll1, text="Immagine già analizzata e dati presenti nel DB")
                self.labelAnalyxed.grid(row=actual_row, columnspan=4, pady=2)
                actual_row += 1
                actual_row = self.show_info(result[0], actual_row)
            else:
                if self.labelAnalyxed is not None:
                    self.labelAnalyxed.grid_remove()
                self.labelAnalyxed = ctk.CTkLabel(self.scroll1, text="Immagine non ancora analizzata")
                self.labelAnalyxed.grid(row=actual_row, columnspan=4)
                actual_row += 1
                self.analisys = ctk.CTkButton(self.scroll1, command=lambda:self.start_analisys(self.filepath), text="Analizza")
                self.analisys.grid(row=actual_row, columnspan = 4, pady = 10)  
        elif self.filepath:
            messagebox.showerror("Errore", "Non puoi selezionare file fuori dalla cartella tessuti!")

    #avvio acquisizione vetrino
    def startAcquisition(self):
        req = {"request":"acquisition"}
        self.message_queue.put(req)
        self.acquire.configure(state='disabled')
    
    #funzione per gestione interfaccia per il salvataggio di immagini di vetrini acquisite con LabSpec
    def save_image(self, img):
        img_ridotta = img.copy()
        img_ridotta.thumbnail((1000, 500))
        photo = ctk.CTkImage(light_image=img_ridotta, size=(1000, 500))
        label = ctk.CTkLabel(self.scroll1, image=photo, text="")
        label.grid(row=4, columnspan = 4, padx=3)
        label.image = photo

        if self.analisys is not None:
            self.analisys.grid_remove()
        
        self.analisys = ctk.CTkButton(self.scroll1, command=lambda:self.start_analisys(self.filepath), text="Analizza")
        self.analisys.grid(row=5, column=0, columnspan = 2, pady = 10, sticky='e', padx=10)
        self.analisys.configure(state='disabled')
        self.saveImg = ctk.CTkButton(self.scroll1, command=lambda:self.save(img), text="Salva")
        self.saveImg.grid(row=5, column=2, columnspan = 2, pady = 10, sticky='w', padx=10)
    
    #salvataggio di un nuovo vetrino
    def save(self,img):
        dirSample = os.path.join(os.getcwd(), "tessuti")
        self.filepath = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")], initialdir = dirSample)
        if self.filepath and os.path.commonpath([dirSample, self.filepath]) == dirSample:
            img.save(self.filepath)
            self.analisys.configure(state='normal')
        else: 
            messagebox.showerror("Errore", "Non puoi selezionare file fuori dalla cartella tessuti!")

    #avvio dell'analisi
    def start_analisys(self, filepath):
        self.analisys.configure(state="disabled")
        if self.matchSlide is not None:
            self.matchSlide.configure(state="disabled")
        thread = threading.Thread(target=self.async_analisys, args=(filepath,))
        thread.start()
    
    def async_analisys(self, filepath):
        slide_analisys(filepath)
        self.ctk.after(0, self.update_analisys, filepath)
    
    #funzione per aggiornamento database una volta terminata l'analisi
    def update_analisys(self, filepath):
       
        self.cursor.close()
        self.cursor = conn.cursor(dictionary=True)
        relative_path = os.path.relpath(filepath,  os.getcwd())
        while True:
            self.cursor.execute("SELECT * FROM Slide WHERE Filepath = %s", (relative_path,))
            result = self.cursor.fetchall()
            
            if len(result)>0:
                break
            time.sleep(0.2)
        
        if result:
            self.analisys.grid_forget()
            self.show_info(result[0], 6)
        else:
            ctk.CTkLabel(self.scroll1, text="Qualcosa è andato storto").grid(row=5, columnspan=4)  
    
    #aggiornamento dell'interfaccia dai dati ottenuti dal db dopo analisi
    def show_info(self, result, actual_row):
        self.info = ctk.CTkFrame(self.scroll1)
        self.info.grid(row=actual_row, column=0, columnspan=4, sticky="nsew")
        for i in range(8):
            self.info.grid_columnconfigure(i, weight=1)
        actual_row = 0
        self.cursor.execute("SELECT * FROM Pattern WHERE Slide = %s", (result["Filepath"],))
        query = self.cursor.fetchall()
        print(len(query))
        idx = 0
        if len(query)==1:
            col = 2
        else:
            col=0
        start_row = actual_row
        for row in query:
            actual_row = start_row 
            ctk.CTkLabel(self.info, text="Campione "+ str(idx + 1), font=("Helvetica", 18), text_color="blue").grid(row=actual_row, column=col, columnspan = 4, pady=5)
            actual_row += 1
            self.labelAndData("X minimo:", str(row["x_min"]), actual_row, col)
            self.labelAndData("Y minimo:", str(row["y_min"]), actual_row, col + 2) 
            actual_row += 1
            self.labelAndData("X massimo:", str(row["x_max"]), actual_row, col)
            self.labelAndData("Y massimo:", str(row["y_max"]), actual_row, col + 2)
            actual_row += 1
            self.labelAndData("Centroide:", "(" + str(row["x_centr"]* MICRONx_x5//PIXEL_IMG_x) + ", " + str(row["y_centr"]* MICRONy_x5//PIXEL_IMG_y) + ")", actual_row, col)
            actual_row += 1
            
            idx += 1
            col += 4

        var = ctk.BooleanVar()
        check = ctk.CTkCheckBox(self.info, text="Utilizza NanoGPS", variable=var)
        check.grid(row = actual_row, columnspan=8)
        if result["NanoGPS"] == 0:
            check.configure(state="disabled")
        actual_row += 1

        self.analisys = ctk.CTkButton(self.info, command=lambda:self.start_analisys(self.filepath), text="Analizza")
        self.analisys.grid(row=actual_row, column = 0, columnspan=4, pady = 10, sticky='e', padx=10)
        self.analisys.configure(state="normal")
        self.matchSlide = ctk.CTkButton(self.info, command=lambda:self.start_slide_match(result["ContourPath"], result["Filepath"]), text="Match campioni")
        self.matchSlide.grid(row=actual_row, column = 4, columnspan=4, pady = 10, sticky='w', padx=10)
        if(len(query)!=2):
            self.matchSlide.configure(state="disabled")

    #funzione di supporto per disegno UI
    def labelAndData(self, label, data, actual_row, col):
        ctk.CTkLabel(self.info, text=label).grid(row=actual_row, column=col, pady=2,  padx=5)
        ctk.CTkLabel(self.info, text=data).grid(row=actual_row, column=col+1, pady=2, padx=5)
    
    #per far partire il matching in quei vetrini dove ci sono 2 campioni
    def start_slide_match(self, path_cnt, filepath):
        self.img1 = path_cnt
        self.img2 = path_cnt
       
        self.notebook.select(self.frame2)
        self.setPattern(filepath, 1)
        self.setPattern(filepath, 2)
        self.check_img()

    #FUNZIONI CHE POSSONO ESSERE ATTIVATE NEL SECONDO NOTEBOOK PER IL MATCHING

    #funzione per prendere vetrino da file system
    def open_file_preview(self, idx):
        dirSample = os.path.join(os.getcwd(), "tessuti")
        filepath = filedialog.askopenfilename(initialdir=dirSample)  # Apri la finestra di dialogo per selezionare un file
        if filepath and os.path.commonpath([dirSample, filepath]) == dirSample: 
            relative_path = os.path.relpath(filepath,  os.getcwd())
            self.ctk.after(0, self.setPattern, relative_path, idx)

    #settaggio di alcuni parametri per il matching attaverso accesso a database e definizione interfaccia
    def setPattern(self, filepath, idx):
        
        self.notebook.tab(self.frame3, state="disabled")
        if hasattr(self, "matchingUI") and self.matchingUI is not None:
            for widget in self.matchingUI.winfo_children():
                widget.destroy()
            self.matchingUI.destroy()
            self.matchingUI = None
        self.cursor.execute("SELECT * FROM Slide WHERE Filepath = %s", (filepath,))
        result = self.cursor.fetchall()
        
        if result:
            self.cursor.execute("SELECT * FROM Pattern WHERE Slide = %s", (result[0]["Filepath"],))
            query = self.cursor.fetchall()
            query.sort(key=lambda x: x["x_min"])

            if idx == 1 and len(query)==1 and query[0]["Colored"]==0:
                messagebox.showerror("Errore", "Seleziona un campione colorato")
                return
            elif idx == 1 and len(query)==2 and query[0]["Colored"]==0 and query[1]["Colored"]==0:
                messagebox.showerror("Errore", "Seleziona un campione colorato")
                return
            if idx == 2 and len(query)==1 and query[0]["Colored"]==1:
                messagebox.showerror("Errore", "Seleziona un campione naturale")
                return
            elif idx == 2 and len(query)==2 and query[0]["Colored"]==1 and query[1]["Colored"]==1:
                messagebox.showerror("Errore", "Seleziona un campione naturale")
                return
            try:
                dirSample = os.path.join(os.getcwd(), filepath)
                img = Image.open(dirSample)
                img.thumbnail((250, 250))  # Riduce mantenendo le proporzioni
            except Exception:
                if idx == 1:
                    self.label1.configure(text="Immagine non valida")
                else:
                    self.label2.configure(text="Immagine non valida")
                    return -1

            if not hasattr(self, 'label_chooseL'):
                self.label_chooseL = ctk.CTkLabel(self.scroll2, text="Scegli un campione del primo vetrino:")
                self.label_chooseL.grid(row=5,column=0)
                self.label_chooseL1 = ctk.CTkRadioButton(self.scroll2, text="Campione sinistro", variable=self.scelta1, value="A")
                self.label_chooseL1.grid(row=5, column=1)
                self.label_chooseL2 = ctk.CTkRadioButton(self.scroll2, text="Campione destro", variable=self.scelta1, value="B")
                self.label_chooseL2.grid(row=5, column=2)
                self.label_chooseR = ctk.CTkLabel(self.scroll2, text="Scegli un campione del secondo vetrino:")
                self.label_chooseR.grid(row=6,column=0)
                self.label_chooseR1 = ctk.CTkRadioButton(self.scroll2, text="Campione sinistro", variable=self.scelta2, value="A")
                self.label_chooseR1.grid(row=6, column=1)
                self.label_chooseR2 = ctk.CTkRadioButton(self.scroll2, text="Campione destro", variable=self.scelta2, value="B")
                self.label_chooseR2.grid(row=6, column=2)
            
            if idx == 1 and len(query)==2 and query[0]["Colored"]==1 and query[1]["Colored"]==0:
                self.scelta1.set("A")
                self.label_chooseL1.configure(state='disabled')
                self.label_chooseL2.configure(state='disabled')
            elif idx == 1 and len(query)==2 and query[0]["Colored"]==0 and query[1]["Colored"]==1:
                self.scelta1.set("B")
                self.label_chooseL1.configure(state='disabled')
                self.label_chooseL2.configure(state='disabled')

            if idx == 2 and len(query)==2 and query[0]["Colored"]==1 and query[1]["Colored"]==0:
                self.scelta2.set("B")
                self.label_chooseR1.configure(state='disabled')
                self.label_chooseR2.configure(state='disabled')
            elif idx == 1 and len(query)==2 and query[0]["Colored"]==0 and query[1]["Colored"]==1:
                self.scelta2.set("A")
                self.label_chooseR1.configure(state='disabled')
                self.label_chooseR2.configure(state='disabled')
                
            
            photo = ctk.CTkImage(light_image=img, size=(200, 100))
            label = ctk.CTkLabel(self.scroll2, image=photo, text="")
            
            if idx == 1:
                self.img1 = result[0]["ContourPath"]
                self.saveImg1 =  os.path.join(os.getcwd(), filepath.split(".")[0])
                label.grid(row=2, column = 2)
                self.filepath_var1 = ctk.StringVar()
                self.filepath_var1.set(filepath)
                self.label1.configure(textvariable=self.filepath_var1)
            else:
                self.img2 =  result[0]["ContourPath"]
                self.saveImg2 =  os.path.join(os.getcwd(), filepath.split(".")[0])
                label.grid(row=4, column=2)
                self.filepath_var2 = ctk.StringVar()
                self.filepath_var2.set(filepath)
                self.label2.configure(textvariable=self.filepath_var2)
            label.image = photo
            
            if idx == 1 and len(query)==1:
                self.x_min1A = query[0]["x_min"]
                self.y_min1A = query[0]["y_min"]
                self.x_max1A = query[0]["x_max"]
                self.y_max1A = query[0]["y_max"]
                self.label_chooseL1.configure(state='disabled')
                self.label_chooseL2.configure(state='disabled')
                self.scelta1.set("A")
            elif idx==2 and len(query)==1:
                self.x_min2A = query[0]["x_min"]
                self.y_min2A = query[0]["y_min"]
                self.label_chooseR1.configure(state='disabled')
                self.label_chooseR2.configure(state='disabled')
                self.scelta2.set("A")
            elif idx == 1 and len(query)==2:
                self.x_min1A = query[0]["x_min"]
                self.y_min1A = query[0]["y_min"]
                self.x_max1A = query[0]["x_max"]
                self.y_max1A = query[0]["y_max"]
                self.x_min1B = query[1]["x_min"]
                self.y_min1B = query[1]["y_min"]
                self.x_max1B = query[1]["x_max"]
                self.y_max1B = query[1]["y_max"]

                self.label_chooseL1.configure(state='normal')
                self.label_chooseL2.configure(state='normal')
            elif idx==2 and len(query)==2:
                self.x_min2A = query[0]["x_min"]
                self.y_min2A = query[0]["y_min"]
                self.x_min2B = query[1]["x_min"]
                self.y_min2B = query[1]["y_min"]

                self.label_chooseR1.configure(state='normal')
                self.label_chooseR2.configure(state='normal')

            if self.img1 != None and self.img2 != None:
                self.matchButton = ctk.CTkButton(self.scroll2, text="Confronta", command=lambda:self.check_img())
                self.matchButton.grid(row=7, columnspan = 3, pady=7)
            if(len(query)==0):
                if idx == 1:
                    self.label1.configure(text="Analisi del fine non ancora eseguita")
                else:
                    self.label2.configure(text="Analisi del file non ancora eseguita")

    #funzione per la verifica che tutti i parametri necessari del matching siano definiti
    def check_img(self):
        
        if self.img1 is not None or self.img2 is not None:
            self.img1 = os.path.normpath(self.img1)
            self.img2 = os.path.normpath(self.img2)
            self.disableButtons()

            patternImg1 = self.scelta1.get()
            patternImg2 = self.scelta2.get()
            filepath1 = self.filepath_var1.get()
            filepath2 = self.filepath_var2.get()

            self.cursor.execute("SELECT * FROM Pattern WHERE Slide = %s", (filepath1,))
            query = self.cursor.fetchall()
            query.sort(key=lambda x: x["x_min"])
            if patternImg1 == "A":
                self.x_min1 = self.x_min1A
                self.y_min1 = self.y_min1A
                self.x_max1 = self.x_max1A
                self.y_max1 = self.y_max1A
                self.treeJson = json.loads(query[0]["images_tree"])
                self.pattIdx = query[0]["ID"] 
            else:
                self.x_min1 = self.x_min1B
                self.y_min1 = self.y_min1B
                self.x_max1 = self.x_max1B
                self.y_max1 = self.y_max1B
                self.treeJson = json.loads(query[1]["images_tree"])
                self.pattIdx = query[1]["ID"] 

            self.cursor.execute("SELECT * FROM Pattern WHERE Slide = %s", (filepath2,))
            query = self.cursor.fetchall()
            query.sort(key=lambda x: x["x_min"])
            if patternImg2 == "A":
                self.x_min2 = self.x_min2A 
                self.y_min2 = self.y_min2A 
            else:
                self.x_min2 = self.x_min2B 
                self.y_min2 = self.y_min2B 

            thread = threading.Thread(target=self.match, args=(patternImg1, patternImg2))
            thread.start()
            
    def disableButtons(self):
        if self.matchButton is not None:
            self.matchButton.configure(state="disabled")
        if self.matchSlide is not None:
            self.matchSlide.configure(state="disabled")
        if self.ramanAcquisition is not None:
            self.ramanAcquisition.configure(state='disabled')
        if self.coloredButton is not None:
            self.coloredButton.configure('disabled')
        if self.naturalButton is not None:
            self.naturalButton.configure('disabled')

    #aggiornamento bottoni : DA INDIVIDUARE DOVE METTERLO
    def enableButtons(self):
        if self.matchButton is not None:
            self.matchButton.configure(state="normal")
        if self.matchSlide is not None:
            self.matchSlide.configure(state="normal")
        if self.ramanAcquisition is not None:
            self.ramanAcquisition.configure(state='normal')
            self.highResolution.configure('normal')
        if self.coloredButton is not None:
            self.coloredButton.configure('normal')
        if self.naturalButton is not None:
            self.naturalButton.configure('normal')

    #avvio del matching tra i vetrini selezionati
    def match(self, patternImg1, patternImg2):
        
        process = match_pattern(self.img1, self.img2, patternImg1, patternImg2) 
        
        if process[0] == 0:
            
            with self.lock:
                self.contourRot = process[1]
                self.iouRot = process[10]
                self.bestRot = process[10]
                self.centr1 = (int(process[2]), int(process[3]))
                self.centr2 = (int(process[4]), int(process[5]))
            cnt1 = process[6]
            cnt2 = process[7]
            width = int(process[8])
            height = int(process[9])

            contour1 = np.array(cnt1, dtype=np.int32).reshape(-1, 1, 2)
            contour2 = np.array(cnt2, dtype=np.int32).reshape(-1, 1, 2)

            self.ctk.after(0, self.update_ui, contour1, contour2, width, height, patternImg1, patternImg2)
        
        self.ctk.after(0, self.enableButtons)

    #aggiornamento interfaccia una volta completato il matching per mostrare i risultati
    def update_ui(self, contour1, contour2, width, height, patternImg1, patternImg2):
        
        if hasattr(self, 'matchingUI') and self.matchingUI is not None:
            self.matchingUI.destroy()
        self.matchingUI = ctk.CTkFrame(self.scroll2)
        
        for i in range(6):
            self.matchingUI.grid_rowconfigure(i, weight=1)

        for j in range(4):
            self.matchingUI.grid_columnconfigure(j, weight=1)

        self.x_trasl = int((self.centr2[0] - self.centr1[0]) * MICRONx_x5/PIXEL_IMG_x)
        self.y_trasl = int((self.centr2[1] - self.centr1[1]) * MICRONy_x5/PIXEL_IMG_y)
        
        self.matchingUI.grid(row=8, column=0, columnspan=3, pady=10)
        ctk.CTkLabel(self.matchingUI, text="Migliore associazione trovata", font=("Helvetica", 30), text_color="blue").grid(row=0, column=0, columnspan=4, pady=8, padx=24)
        ctk.CTkLabel(self.matchingUI, text="Rotazione basata su bordi:").grid(row=2, column=0, pady=2, padx=8)
        ctk.CTkLabel(self.matchingUI, text=str(self.contourRot)).grid(row=3, column=0, pady=2, padx=8)
        
        ctk.CTkLabel(self.matchingUI, text="Rotazione basata su IoU").grid(row=2, column=1)
        ctk.CTkLabel(self.matchingUI, text=str(self.iouRot)).grid(row=3, column=1, pady=2, padx=8)
        ctk.CTkLabel(self.matchingUI, text="Traslazione").grid(row=2, column=2)
        ctk.CTkLabel(self.matchingUI, text=f"({str(self.x_trasl)}, {str(self.y_trasl)})").grid(row=3, column=2, pady=2, padx=8)
        ctk.CTkLabel(self.matchingUI, text="Rotazione").grid(row=2, column=3)

        ctk.CTkLabel(self.matchingUI, text="Clicca nel primo vetrino per visualizzare corrispondenza").grid(row=4, column=1, columnspan=2, padx=8)

        self.vetr1 = ctk.CTkLabel(self.matchingUI, text="Corrispondenza vetrino 1")
        self.vetr1.grid(row=5, column=1, columnspan=2, pady=2)
        self.vetr2 = ctk.CTkLabel(self.matchingUI, text="Corrispondenza vetrino 2")
        self.vetr2.grid(row=6, column=1, columnspan=2, pady=2)

        #self.defaultX = tk.StringVar()
        #self.defaultY = tk.StringVar()
        #self.defaultX.set(self.x_trasl)
        #self.defaultY.set(self.y_trasl)
        
        self.defaultRot = tk.StringVar()
        self.defaultRot.set(self.bestRot)
        #self.defaultRot.trace_add("write", lambda *args:self.drawImg(self.matchingUI, contour1, contour2, width, height))

        #x = tk.Spinbox(self.matchingUI, from_=self.x_trasl, to=self.x_trasl, textvariable=self.defaultX, command=self.update_match)
        #y = tk.Spinbox(self.matchingUI, from_=self.y_trasl, to=self.y_trasl, textvariable=self.defaultY, command=self.update_match)
        rot = tk.Spinbox(self.matchingUI, from_=0.0, to=359.9, increment=0.1, textvariable=self.defaultRot, format="%.1f", command=lambda:self.drawImg(self.matchingUI, contour1, contour2, width, height))
        rot.bind(
            "<Return>",
            lambda event: self.drawImg(self.matchingUI, contour1, contour2, width, height)
        )
        #x.grid(row=3, column=1)
        #y.grid(row=3, column=2)
        rot.grid(row = 3, column=3)
        ctk.CTkLabel(self.matchingUI, text="").grid(row=7, column=1, columnspan=2, pady = 100)

        if patternImg1 == "A":
            path1 = self.saveImg1 + "_pattern0.jpg"
        else:
            path1 = self.saveImg1 + "_pattern1.jpg"

        resized_width = 500

        if patternImg2 == "A":
            path2 = self.saveImg2 + "_pattern0.jpg"
        else:
            path2 = self.saveImg2 + "_pattern1.jpg"

        self.drawImg(self.matchingUI, contour1, contour2, width, height) #disegno le associazioni
        
        img1 = Image.open(path1)
        width1, height1 = img1.size

        img2 = Image.open(path2)
        width2, height2 = img2.size

        scale_ratio1 = resized_width / width1   
        scale_ratio2 = resized_width / width2

        common_scale_ratio = min(scale_ratio1, scale_ratio2)

        new_width1 = int(width1 * common_scale_ratio)
        new_height1 = int(height1 * common_scale_ratio)

        new_width2 = int(width2 * common_scale_ratio)
        new_height2 = int(height2 * common_scale_ratio)

        img1_resized = img1.resize((new_width1, new_height1), Image.Resampling.LANCZOS)
        img2_resized = img2.resize((new_width2, new_height2), Image.Resampling.LANCZOS)

        self.tk_img1 = ImageTk.PhotoImage(img1_resized)
        self.tk_img2 = ImageTk.PhotoImage(img2_resized)

        target_width = max(new_width1, new_width2)
        target_height = max(new_height1, new_height2)

        if hasattr(self, 'canvasPatt1'):
            self.canvasPatt1.destroy()
            self.canvasPatt2.destroy()

        self.canvasPatt1 = tk.Canvas(self.matchingUI, width=target_width, height=target_height)
        self.canvasPatt1.grid(row=4, column=0, rowspan=4)

        self.canvasPatt2 = tk.Canvas(self.matchingUI, width=target_width, height=target_height)
        self.canvasPatt2.grid(row=4, column=3, rowspan=4)

        self.offset_y1 = (target_height - new_height1) // 2
        self.offset_y2 = (target_height - new_height2) // 2
        self.offset_x1 = (target_width - new_width1) // 2
        self.offset_x2 = (target_width - new_width2) // 2

        self.canvasPatt1.create_image(self.offset_x1, self.offset_y1, anchor="nw", image=self.tk_img1)
        self.canvasPatt2.create_image(self.offset_x2, self.offset_y2, anchor="nw", image=self.tk_img2)

        self.canvasPatt1.bind("<Button-1>", lambda event: self.pick_point(event, common_scale_ratio))
        ctk.CTkButton(self.matchingUI, text="Acquisizione Raman", command=lambda:self.acq_raman(), font=("Helvetica", 12)).grid(row=8, column=0, columnspan=4, padx=4)

    #disegno della sovrapposizione dei contorni e dei due campioni confrontati ruotati del valore indicato
    def drawImg(self, frame, contour1, contour2, width, height):
        
        self.bestRot = float(self.defaultRot.get())

        if hasattr(self, 'contours'):
            self.contours.get_tk_widget().destroy()

        if hasattr(self, 'overlap'):
            self.overlap.get_tk_widget().destroy()
        
        contour2 = contour2 - self.centr2 + self.centr1
        
        rotMatrix = cv2.getRotationMatrix2D(self.centr1, -self.bestRot, 1.0)
        new_contour = cv2.transform(contour2, rotMatrix)
        img = np.zeros((height,width), dtype=np.uint8)
        cv2.drawContours(img, [contour1], -1, 255, 7)
        cv2.drawContours(img, [new_contour], -1, 7)
        coords = cv2.findNonZero(img)
        x_min = coords[:, 0, 0].min()
        y_min = coords[:, 0, 1].min()
        x_max = coords[:, 0, 0].max()
        y_max = coords[:, 0, 1].max()

        img = np.zeros((height,width, 3), dtype=np.uint8)
        cv2.drawContours(img, [contour1], -1, (0, 255, 0), 7)
        cv2.drawContours(img, [new_contour], -1, (255,0,0), 7)
        img = img[y_min:y_max, x_min:x_max]

        #calcolo intersection over union
        mask1 = np.zeros((height, width), dtype=np.uint8)
        mask2 = np.zeros((height, width), dtype=np.uint8)

        cv2.drawContours(mask1, [contour1], -1, 255, -1)
        cv2.drawContours(mask2, [new_contour], -1, 255, -1)

        intersection = cv2.bitwise_and(mask1, mask2)
        union = cv2.bitwise_or(mask1, mask2)

        iou = np.sum(intersection > 0) / np.sum(union > 0)
        print("IoU:", iou)

        #fine calcolo

        fig, ax = plt.subplots()
        ax.axis('off')
        ax.imshow(img) 

        self.contours = FigureCanvasTkAgg(fig, master=frame)
        self.contours.draw()
        self.contours.get_tk_widget().grid(row = 1, column=0, columnspan=2, padx=2)

        contourImg1 = np.zeros((height,width), dtype=np.uint8)
        cv2.drawContours(contourImg1, [contour1], -1, 1)

        contour2 = contour2 - self.centr1 + self.centr2
        contourImg2 = np.zeros((height,width), dtype=np.uint8)
        cv2.drawContours(contourImg2, [contour2], -1, 1)

        ys, xs = np.where(contourImg1 > 0)
        if len(ys) == 0:
            print("Nessun pixel bianco trovato")
        else:
            min_y = ys.min()
            min_x = xs.min()
            max_y = ys.max()
            max_x = xs.max()

        img1 = cv2.imread(self.saveImg1 + ".jpg")
        img1 = img1[min_y:max_y, min_x:max_x]
        h1, w1 = img1.shape[:2]

        ys, xs = np.where(contourImg2 > 0)
        if len(ys) == 0:
            print("Nessun pixel bianco trovato")
        else:
            min_y = ys.min()
            min_x = xs.min()
            max_y = ys.max()
            max_x = xs.max()
             
        img2 = cv2.imread(self.saveImg2 + ".jpg")

        rotated_img2 =  rotate_image_center(img2, -self.bestRot)  
        rotated_contour = rotate_image_center(contourImg2, -self.bestRot)  

        ys, xs = np.where(rotated_contour > 0)
        min_y = ys.min()
        min_x = xs.min()

        rotated_img2_cropped = rotated_img2[min_y:min_y + h1, min_x:min_x + w1]

        img1_color = np.zeros_like(img1)
        img2_color = np.zeros_like(rotated_img2_cropped)

        img1_color[:, :, 2] = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY) #verde
        img2_color[:, :, 1] = cv2.cvtColor(rotated_img2_cropped, cv2.COLOR_BGR2GRAY) #rosso

        print("img1_color shape:", img1_color.shape)
        print("img2_color shape:", img2_color.shape)

        overlap = cv2.addWeighted(img1_color, 1.0, img2_color, 1.0, 0)

        fig, ax = plt.subplots()
        ax.axis('off')
        ax.imshow(cv2.cvtColor(overlap, cv2.COLOR_BGR2RGB))
        ax.set_aspect('auto')

        self.overlap = FigureCanvasTkAgg(fig, master=frame)
        self.overlap.draw()
        self.overlap.get_tk_widget().grid(row=1, column=2, columnspan=2, padx=2)

    #seleziona un punto in un campione per poi visualizzarlo in quella colorata corrispondente
    def pick_point(self, event, common_scale_ratio):
        
        if hasattr (self, 'oval1'):
            self.canvasPatt1.delete(self.oval1)
        x1, y1 = event.x, event.y

        r = 3
        self.oval1 = self.canvasPatt1.create_oval(x1 - r, y1 - r, x1 + r, y1 + r, fill="red", outline="red")
        
        x_orig = int(((x1 - self.offset_x1) * MICRONx_x5 / PIXEL_IMG_x) / common_scale_ratio + self.x_min1)
        y_orig = int(((y1 - self.offset_y1) * MICRONy_x5 / PIXEL_IMG_y) / common_scale_ratio + self.y_min1)
        point = np.array([x_orig, y_orig], dtype=np.float32)
        self.vetr1.configure(text=f"Corrispondenza vetrino 1: ({int(point[0])}, {int(point[1])})")
        self.submit(point, common_scale_ratio)

    #aggiornamento interfaccia e calcolo del punto corrispettivo su campione non colorato
    def submit(self, point, common_scale_ratio):
        
        center = (int((self.centr1[0] * MICRONx_x5 / PIXEL_IMG_x)), 
                  int((self.centr1[1] * MICRONy_x5 / PIXEL_IMG_y)))

        rotMatrix = cv2.getRotationMatrix2D(center, self.bestRot, 1.0)  
        rotated_point = cv2.transform(np.array([[point]], dtype=np.float32), rotMatrix)[0][0]

        final_point = rotated_point + (self.x_trasl, self.y_trasl)
        print(point, final_point)

        r = 3
        canvas_x = int(((final_point[0] - self.x_min2)*PIXEL_IMG_x/MICRONx_x5) * common_scale_ratio) + self.offset_x2
        canvas_y = int(((final_point[1] - self.y_min2)*PIXEL_IMG_y/MICRONy_x5) * common_scale_ratio) + self.offset_y2
        print(canvas_x, canvas_y)
        
        if hasattr(self, 'oval2'):
            self.canvasPatt2.delete(self.oval2)
        self.oval2 = self.canvasPatt2.create_oval(canvas_x - r, canvas_y - r, canvas_x + r, canvas_y + r, fill="green", outline="green")
        self.vetr2.configure(text=f"Corrispondenza vetrino 2: ({int(final_point[0])}, {int(final_point[1])})")

        self.scroll2.focus_set()

    #QUESTE SONO FUNZIONI CHE RIGUARDANO IL TERZO NOTEBOOK PER FARE RAMAN

    #definizione dell'interfaccia iniziale con immagine da dove acquisire
    def acq_raman(self):
        
        self.rect = None
        self.oval = None
        self.start_x = None
        self.start_y = None

        self.notebook.tab(self.frame3, state="normal")
        self.notebook.select(self.frame3)
        ctk.CTkLabel(self.scroll3, text="Acquisizione Raman", font=("Helvetica", 40), anchor="center", text_color="blue").grid(row=0, column=0, columnspan=2, pady=16)

        container = tk.Frame(self.scroll3)
        container.grid(row=2, column=0, columnspan=2, sticky="nsew")
        ctk.CTkButton(self.scroll3, text="Torna alla mappa completa", command=lambda:self.drawMosaic(), font=("Helvetica", 10)).grid(row=1,column=0,columnspan=2,pady=5)
        self.canvas_frame = tk.Canvas(container, bg="white", height = 720)
        h_scroll = tk.Scrollbar(container, orient="horizontal", command=self.canvas_frame.xview)
        v_scroll = tk.Scrollbar(container, orient="vertical", command=self.canvas_frame.yview)
        self.canvas_frame.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")
        h_scroll.grid(row=1, column=0, sticky="ew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        self.canvas_frame.bind_all("<MouseWheel>", self._on_mousewheel)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.drawMosaic()

        self.canvas_frame.bind("<ButtonPress-1>", self.on_press)
        self.canvas_frame.bind("<B1-Motion>", self.on_drag)
        self.canvas_frame.bind("<ButtonRelease-1>", self.on_release)

        self.distSpectrum = tk.StringVar()
        self.distSpectrum.set(100)

        ctk.CTkLabel(self.scroll3, text="Coordinate corrispettive sul campione naturale").grid(row=3, column=0, padx=8, sticky='e')
        self.coord = ctk.CTkLabel(self.scroll3, text="")
        self.coord.grid(row=3, column=1, padx=8, sticky='w')

        ctk.CTkLabel(self.scroll3, text="Distanza acquisizione spettri").grid(row=5, column=0)
        spect = tk.Spinbox(self.scroll3, from_=20, to=300, increment=1, textvariable=self.distSpectrum)
        spect.grid(row=5, column=1)
        spect.bind(
            "<Return>",
            lambda event: self.distSpectrum.set(spect.get())
        )

        self.highResolution = ctk.CTkButton(self.scroll3, text="Aumenta risoluzione", command=lambda:self.search_resolution(), font=("Helvetica", 12))
        self.highResolution.grid(row=6, column=0)
        self.ramanAcquisition = ctk.CTkButton(self.scroll3, text="Acquisizione Raman", command=lambda:self.startRaman(), font=("Helvetica", 12))
        self.ramanAcquisition.grid(row=6, column=1, pady=8)

        with self.lock:
            if not self.connAval:
                self.ramanAcquisition.configure(state='disabled')
                self.connectedSignal2 = ctk.CTkLabel(self.scroll3, text="", width=20, height=1, fg_color="red")
                self.connectedSignal2.grid(row=4, column=0, sticky='e', padx=20)
                self.connected2 = ctk.CTkLabel(self.scroll3, text="Spettrometro disconnesso")
                self.connected2.grid(row=4, column=1, pady=3, sticky='w')
            else:
                self.connectedSignal2 = ctk.CTkLabel(self.scroll3, text="", width=20, height=1, fg_color="green")
                self.connectedSignal2.grid(row=4, column=0, sticky='e', padx=20)
                self.connected2 = ctk.CTkLabel(self.scroll3, text="Spettrometro connesso")
                self.connected2.grid(row=4, column=1, pady=3, sticky='w')
    
    def drawMosaic(self):
        self.scope = 5
        img = Image.open(self.saveImg1 + ".jpg")
        x_min = int((self.x_min1) / MICRONx_x5 * PIXEL_IMG_x)
        y_min = int((self.y_min1) / MICRONy_x5 * PIXEL_IMG_y)
        x_max = int((self.x_max1) / MICRONx_x5 * PIXEL_IMG_x)
        y_max = int((self.y_max1) / MICRONy_x5 * PIXEL_IMG_y)
        
        self.offset_x_min = x_min - (x_min % PIXEL_IMG_x)
        self.offset_y_min = y_min - (y_min % PIXEL_IMG_y)
        offset_x_max = x_max - (x_max % PIXEL_IMG_x) + PIXEL_IMG_x
        offset_y_max = y_max - (y_max % PIXEL_IMG_y) + PIXEL_IMG_y
        print(self.offset_x_min, self.offset_y_min)
        img_cropped = img.crop((self.offset_x_min, self.offset_y_min, offset_x_max, offset_y_max))
        photo = ImageTk.PhotoImage(img_cropped)
        self.raman_photo = photo
        self.ramanImage = self.canvas_frame.create_image(0, 0, anchor="nw", image=photo)
        self.canvas_frame.config(scrollregion=(0, 0, img_cropped.width, img_cropped.height))
        self.canvas_frame.config(height=PIXEL_IMG_y*2)

        self.final_img = img_cropped

    #per scorrere l'immagine con il mouse
    def _on_mousewheel(self, event):
        self.canvas_frame.yview_scroll(int(-1 * (event.delta / 120)), "units")

    #funzione per avviare il disegno del rettangolo se si vuole maggiore risoluzione
    def on_press(self, event):
        if self.rect:
            self.canvas_frame.delete(self.rect)
        if self.oval:
            self.canvas_frame.delete(self.oval)
        self.start_x = self.canvas_frame.canvasx(event.x) - (self.canvas_frame.canvasx(event.x) % PIXEL_IMG_x)
        self.start_y = self.canvas_frame.canvasy(event.y) - (self.canvas_frame.canvasy(event.y) % PIXEL_IMG_y)
        if self.start_x >= self.final_img.width or self.start_y > self.final_img.height:
            messagebox.showerror("Errore", "Posizione non valida")
            return
        self.rect = self.canvas_frame.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=3)

    #per il disegno in trascinamento 
    def on_drag(self, event):
        current_x = self.canvas_frame.canvasx(event.x) 
        current_y = self.canvas_frame.canvasy(event.y)
        if current_x < self.start_x or current_y < self.start_y:
            return 
        dx = current_x - self.start_x
        dy = current_y - self.start_y
        size = min(abs(dx), abs(dy))

        end_x = self.start_x + (size if dx >= 0 else -size)
        end_y = self.start_y + (size if dy >= 0 else -size)

        self.canvas_frame.coords(self.rect, self.start_x, self.start_y, end_x, end_y)

    #disegno finale del rettangolo con memorizzazione delle posizioni
    def on_release(self, event):

        if self.start_x >= self.final_img.width or self.start_y > self.final_img.height:
            return
        
        end_x = self.canvas_frame.canvasx(event.x) + PIXEL_IMG_x 
        end_y = self.canvas_frame.canvasy(event.y) + PIXEL_IMG_y 

        end_x -= end_x % PIXEL_IMG_x 
        end_y -= end_y % PIXEL_IMG_y 
        if self.start_x >= end_x or self.start_y >= end_y:
            return
        if self.canvas_frame.canvasx(event.x) > self.final_img.width:
            end_x = self.final_img.width
        if self.canvas_frame.canvasy(event.y) > self.final_img.height:
            end_y = self.final_img.height
        center_x = (self.start_x + end_x) // 2
        center_y = (self.start_y + end_y) // 2

        self.canvas_frame.coords(self.rect, self.start_x, self.start_y, end_x, end_y)
        r = 6
        self.oval = self.canvas_frame.create_oval(center_x - r, center_y - r, center_x + r, center_y + r, fill="red", outline="red")

        x0, y0, x1, y1 = self.canvas_frame.coords(self.rect)
        with self.lock:
            dirname = os.path.dirname(self.filepath_var2.get())
                                        
        dir = os.path.join(dirname, "Raman_Acquisition") 
        if os.path.exists(dir):
            if self.scope == 5:
                stepX = MICRONx_x5
                stepY = MICRONy_x5 
            elif self.scope == 10:
                stepX = MICRONx_x5 // 2
                stepY = MICRONy_x5 // 2

            self.start_x = int(x0 + self.offset_x_min) * stepX // PIXEL_IMG_x
            self.start_y = int(y0 + self.offset_y_min) * stepY // PIXEL_IMG_y
            self.end_x = int(x1 + self.offset_x_min) * stepX // PIXEL_IMG_x
            self.end_y = int(y1 + self.offset_y_min) * stepY // PIXEL_IMG_y

            point = np.array([self.start_x, self.start_y], dtype=np.float32)
            center = (self.centr1[0] * stepX // PIXEL_IMG_x, self.centr1[1] * stepY // PIXEL_IMG_y)
            rotMatrix = cv2.getRotationMatrix2D(center, self.bestRot, 1.0)
            rotated_point = cv2.transform(np.array([[point]], dtype=np.float32), rotMatrix)[0][0]
            x = int(rotated_point[0] + self.x_trasl) - stepX//2
            y = int(rotated_point[1] + self.y_trasl) - stepY//2
            if self.scope == 5:
                self.coord.configure(text=f"({x}, {y})")
            print(x, y)
            file = os.path.join(dir, f"{x}_{y}.txt")
            if os.path.exists(file):
                self.canvas_frame.itemconfig(self.rect, outline='green')
                self.canvas_frame.itemconfig(self.oval, outline='green', fill='green')
    
    #ricerca di immagini a maggior risoluzione per il rettangolo selezionato
    def search_resolution(self):
        if self.rect is None:
            messagebox.showerror("Errore", "Seleziona prima l'area da acquisire")
            return
        x0, y0, x1, y1 = self.canvas_frame.coords(self.rect)

        if self.scope == 5:
            stepX = MICRONx_x5
            stepY = MICRONy_x5 
            scope = 10
        elif self.scope == 10:
            stepX = MICRONx_x5 // 2
            stepY = MICRONy_x5 // 2
            scope = 50
        else:
            messagebox.showerror("Errore", "Impossibile acquisire a risoluzione maggiore")
            return
        print(stepX, stepY)
        self.start_x = int(x0 + self.offset_x_min) * stepX // PIXEL_IMG_x
        self.start_y = int(y0 + self.offset_y_min) * stepY // PIXEL_IMG_y
        self.end_x = int(x1 + self.offset_x_min) * stepX // PIXEL_IMG_x
        self.end_y = int(y1 + self.offset_y_min) * stepY // PIXEL_IMG_y

        acquired = True
        for i in range (self.start_x, self.end_x, stepX):
            for j in range(self.start_y, self.end_y, stepY):
                with self.lock:
                    if self.treeJson[f"{i}_{j}"]["child"] != []:
                        children = self.treeJson[f"{i}_{j}"]["child"]

                        sorted_children = sorted(children, key=extract_coords)
                        for child in sorted_children:
                            path = os.path.join(os.getcwd(), child["path"])
                            if not os.path.exists(path):
                                self.treeJson[f"{i}_{j}"]["child"] = []
                                break
                            
                    if self.treeJson[f"{i}_{j}"]["child"] == [] and not self.connAval:
                        messagebox.showinfo("Risoluzione", "Risoluzione non disponibile e impossibile avviare acquisizione")
                        return
                    elif self.treeJson[f"{i}_{j}"]["child"] == [] and self.connAval:
                        acquired = False
                        self.acquire.configure(state='disabled')
                        self.ramanAcquisition.configure(state='disabled')
                        req = {"request":"patternAcquisition", "scope":scope, "min_x":i, "min_y":j}
                        self.message_queue.put(req)
        
        if acquired:
            self.createResImage()
    
    #creazione dell'immagine a più alta risoluzione
    def createResImage(self):
        
        self.cursor.execute("SELECT * FROM Pattern WHERE ID = %s", (self.pattIdx,))
        query = self.cursor.fetchone()
        self.treeJson = json.loads(query["images_tree"])

        if self.scope == 5:
            part_x = 2 * PIXEL_IMG_x
            part_y = 2 * PIXEL_IMG_y  
            stepX = MICRONx_x5  
            stepY = MICRONy_x5
            self.scope = 10     
        elif self.scope == 10:
            part_x = 10 * PIXEL_IMG_x
            part_y = 10 * PIXEL_IMG_y
            stepX = MICRONx_x5 // 2
            stepY = MICRONy_x5 // 2
            self.scope = 50

        num_x = (self.end_x - self.start_x) // stepX
        num_y = (self.end_y - self.start_y) // stepY 
        print(num_x)
        dim_x = part_x * num_x
        dim_y = part_y * num_y
        final_img = Image.new('RGB', (dim_x, dim_y))
        x = 0
        y = 0
        for i in range(self.start_x, self.end_x, stepX):
            for j in range(self.start_y, self.end_y, stepY):
                print(self.end_y, i, j)
                partial_img = Image.new('RGB', (part_x, part_y))
                pos_x = 0
                pos_y = 0

                children = self.treeJson[f"{i}_{j}"]["child"]

                sorted_children = sorted(children, key=extract_coords)
                for child in sorted_children:
                    print(child)
                    img = Image.open(child["path"])
                    partial_img.paste(img, (pos_x, pos_y))
                    pos_y += PIXEL_IMG_y
                    if pos_y == part_y:
                        pos_y = 0
                        pos_x += PIXEL_IMG_x
                
                final_img.paste(partial_img, (x, y))
                x += part_x
                if x == dim_x:
                    x = 0
                    y += part_y
        
        self.acquire.configure(state='normal')
        self.ramanAcquisition.configure(state='normal')

        self.offset_x_min = self.start_x
        self.offset_y_min = self.start_y
        
        photo = ImageTk.PhotoImage(final_img)
        self.raman_photo = photo
        self.final_img = final_img
        self.ramanImage = self.canvas_frame.create_image(0, 0, anchor="nw", image=photo)
        self.canvas_frame.update_idletasks()
        current_width = self.canvas_frame.winfo_width()
        print(current_width, final_img.width)
        current_height = self.canvas_frame.winfo_height()
        if final_img.width < current_width:
            self.canvas_frame.config(width=final_img.width)
        if final_img.height < current_height:
            self.canvas_frame.config(height=final_img.height)
        self.canvas_frame.config(scrollregion=(0, 0, final_img.width, final_img.height))

    #avvio dell'acquisizione Raman
    def startRaman(self):
        if not hasattr(self, 'rect') or self.rect is None:
            return
        x0, y0, x1, y1 = self.canvas_frame.coords(self.rect)
        
        if self.scope == 5:
            stepX = MICRONx_x5
            stepY = MICRONy_x5 
        elif self.scope == 10:
            stepX = MICRONx_x5 // 2
            stepY = MICRONy_x5 // 2

        print(stepX, stepY)
        self.start_x = int(x0 + self.offset_x_min) * stepX // PIXEL_IMG_x
        self.start_y = int(y0 + self.offset_y_min) * stepY // PIXEL_IMG_y
        self.end_x = int(x1 + self.offset_x_min) * stepX // PIXEL_IMG_x
        self.end_y = int(y1 + self.offset_y_min) * stepY // PIXEL_IMG_y

        dist = int(self.distSpectrum.get())
        
        print(dist)
        for i in range(self.start_x, self.end_x, dist):
            for j in range(self.start_y, self.end_y, dist):

                point = np.array([i, j], dtype=np.float32)
                center = (self.centr1[0] * stepX // PIXEL_IMG_x, self.centr1[1] * stepY // PIXEL_IMG_y)
                rotMatrix = cv2.getRotationMatrix2D(center, self.bestRot, 1.0)
                rotated_point = cv2.transform(np.array([[point]], dtype=np.float32), rotMatrix)[0][0]
                ramanX = int(rotated_point[0] + self.x_trasl) - stepX//2
                ramanY = int(rotated_point[1] + self.y_trasl) - stepY//2
                req = {"request":"ramanAcquisition", "ramanX":ramanX, "ramanY":ramanY}
                print(ramanX, ramanY)
                self.message_queue.put(req)
                self.highResolution.configure(state='disabled')
                self.disableButtons()
    
    #Funzioni per il quarto notebook e la visualizzazione di spettri
    def open_spectrum(self):
        filepath = filedialog.askopenfilename()  # Apri la finestra di dialogo per selezionare un file

def rotate_image_center(img, angle):
    # Calcola il centro
    h, w = img.shape[:2]
    center = (w // 2, h // 2)

    # Matrice di rotazione
    rot_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

    # Calcola dimensioni canvas sufficiente per contenere tutta la rotazione
    abs_cos = abs(rot_matrix[0, 0])
    abs_sin = abs(rot_matrix[0, 1])
    bound_w = int(h * abs_sin + w * abs_cos)
    bound_h = int(h * abs_cos + w * abs_sin)

    # Aggiusta la matrice per traslare al centro del nuovo canvas
    rot_matrix[0, 2] += bound_w / 2 - center[0]
    rot_matrix[1, 2] += bound_h / 2 - center[1]

    # Ruota su canvas più grande
    rotated = cv2.warpAffine(img, rot_matrix, (bound_w, bound_h), flags=cv2.INTER_LINEAR)

    return rotated


def extract_coords(child):
    filename = os.path.splitext(os.path.basename(child["path"]))[0]  
    parts = filename.split("_")
    x = int(parts[0])
    y = int(parts[1])
    return (x, y)