import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import mysql.connector
import subprocess
import os.path
import json
import threading
#import win32com.client

Image.MAX_IMAGE_PIXELS = None #serve per disattivare limite di sicurezza per grandezza immagini di PIL

# Connessione al database locale
conn = mysql.connector.connect(
    host="localhost",      
    user="root",
    password="Giocondo2021$",
)

cursor = conn.cursor(dictionary=True)

class tkinter:
    def __init__(self):

        #cursor.execute("DROP DATABASE IF EXISTS Raman_DB")
        cursor.execute("CREATE DATABASE IF NOT EXISTS Raman_DB")
        cursor.execute("USE Raman_DB")

        cursor.execute("""CREATE TABLE IF NOT EXISTS Slide(
        Filepath VARCHAR(255) PRIMARY KEY,
        NanoGPS BOOLEAN NOT NULL DEFAULT False,
        x_nano FLOAT,
        y_nano FLOAT,
        ContourPath TEXT
        )""")

        cursor.execute("""
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
            FOREIGN KEY (Slide) REFERENCES Slide(Filepath) 
            )
        """)

        self.tk = tk.Tk()
        self.tk.geometry("800x800")
        self.tk.title("Acquisizioni Raman automatizzate")
        self.tk.grid_rowconfigure(0, weight=1)
        self.tk.grid_columnconfigure(0, weight=1)
        self.tk.grid_columnconfigure(1, weight=1)

        def on_resize(event):
            self.tk.grid_columnconfigure(0, minsize=event.width)
            self.tk.grid_columnconfigure(1, minsize=event.width)

        self.tk.bind("<Configure>", on_resize)

        self.notebook = ttk.Notebook(self.tk)
        self.notebook.pack(expand=True, fill='both')

        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab1.grid_propagate(False)
        self.tab2.grid_propagate(False)
        self.tab1.grid(row=0, column=0, sticky="nsew")
        self.tab2.grid(row=0, column=0, sticky="nsew")

        self.notebook.add(self.tab1, text='Visualizzazione vetrino')
        self.notebook.add(self.tab2, text='Matching campioni')

        self.scroll1 = self.create_frame(self.tab1)
        self.scroll2 = self.create_frame(self.tab2)

        self.scroll1.grid_columnconfigure(0, weight=1)
        self.scroll1.grid_columnconfigure(1, weight=1)

        self.scroll2.grid_columnconfigure(0, weight=1)
        self.scroll2.grid_columnconfigure(1, weight=1)
        self.scroll2.grid_columnconfigure(2, weight=1)

        self.img1 = None
        self.img2 = None
        self.matchButton = None
        self.analisys = None
        self.matchSlide = None
        self.scelta1 = tk.StringVar()
        self.scelta2 = tk.StringVar()
        self.scelta1.set("A")
        self.scelta2.set("A")
        
        tk.Label(self.scroll1, text="Visualizzazione vetrino", fg = "blue", font=("Helvetica", 30), anchor="center").grid(row=1, columnspan=2, pady = 8)
        tk.Label(self.scroll1, text="Carica un campione da disco oppure inizia un acquisizione con il microspettrometro LabSpec6").grid(row=2, columnspan=2, pady=4)
        tk.Button(self.scroll1, text="Carica", command=lambda:self.open_file()).grid(row=3, column = 0,  padx = 5, pady = 8)
        self.acquire = tk.Button(self.scroll1,  command=lambda:self.startAcquisition(), text="Acquisisci")
        self.acquire.grid(row=3, column = 1, padx = 5, pady = 8)

        tk.Label(self.scroll2, text="Matching campioni", fg = "blue", font=("Helvetica", 30)).grid(row=1, columnspan=3, pady = 10)
        tk.Button(self.scroll2, text="Scegli campione 1", command=lambda:self.open_file_preview(1)).grid(row=2, column = 0, pady = 50)
        self.label1 = tk.Label(self.scroll2, text="Nessun Path selezionato al momento", anchor='w')
        self.label1.grid(row=2, column=1, sticky='w')
        tk.Label(self.scroll2, text="").grid(row=3, pady=4)
        tk.Button(self.scroll2, text="Scegli campione 2", command=lambda:self.open_file_preview(2)).grid(row=4, column = 0, pady =50)
        self.label2 = tk.Label(self.scroll2, text="Nessun Path selezionato al momento", anchor='w')
        self.label2.grid(row=4, column=1, sticky='w')

    def startAcqusition(self):
        vbs_path = r"D:\Giorgio\Unipi\Tirocinio\VBScript\13062025.vbs"
        subprocess.run(['cscript.exe', vbs_path], check=True)
        #labspec = None
        #try:
            #labspec = win32com.client.Dispatch("LabSpec6.Application")
            #print("Connesso a LabSpec6")
        #except Exception as e:
            #print(f"Errore nella connessione: {e}")
            #tk.Label(self.scroll2, text="Impossibile connettersi a LabSpec6").grid(row = 4, column=0, columnspan=2)
            #return
        

            

    def open_file_preview(self, idx):
        filepath = filedialog.askopenfilename()
        if filepath:
            cursor.execute("SELECT * FROM Slide WHERE Filepath = %s", (filepath,))
            result = cursor.fetchall()
            
            if result:
                try:
                    img = Image.open(filepath)
                    img.thumbnail((250, 250))  # Riduce mantenendo le proporzioni
                except Exception:
                    if idx == 1:
                        self.label1.grid_remove()
                        self.label1 = tk.Label(self.scroll2, text="Immagine non valida")
                        self.label1.grid(row=2, column=1, sticky='w')
                    else:
                        self.label2.grid_remove()
                        self.label2 = tk.Label(self.scroll2, text="Immagine non valida")
                        self.label2.grid(row=4, column=1, sticky='w')
                    return -1

                if self.matchButton is not None:
                    self.label_chooseL.grid_forget()
                    self.label_chooseL1.grid_forget()
                    self.label_chooseL2.grid_forget()
                    self.label_chooseR.grid_forget()
                    self.label_chooseR1.grid_forget()
                    self.label_chooseR2.grid_forget()
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(self.scroll2, image=photo)
                filepath_var = tk.StringVar()
                filepath_var.set(filepath)
                if idx == 1:
                    self.img1 = result[0]["ContourPath"]
                    self.label1.grid_remove()
                    label.grid(row=2, column = 2)
                    self.label1 = tk.Label(self.scroll2, textvariable=filepath_var)
                    self.label1.grid(row=2, column=1, sticky='w')
                else:
                    self.img2 = result[0]["ContourPath"]
                    self.label2.grid_remove()
                    label.grid(row=4, column=2)
                    self.label2 = tk.Label(self.scroll2, textvariable=filepath_var)
                    self.label2.grid(row=4, column=1, sticky='w')
                label.image = photo

                cursor.execute("SELECT * FROM Pattern WHERE Slide = %s", (result[0]["Filepath"],))
                query = cursor.fetchall()
                
                if len(query)==2 and idx == 1:
                    self.label_chooseL = tk.Label(self.scroll2, text="Scegli un campione del primo vetrino:").grid(row=5,column=0)
                    self.label_chooseL1 = tk.Radiobutton(self.scroll2, text="Campione sinistro", variable=self.scelta1, value="A").grid(row=5, column=1)
                    self.label_chooseL2 = tk.Radiobutton(self.scroll2, text="Campione destro", variable=self.scelta1, value="B").grid(row=5, column=2)
                elif len(query)==2 and idx == 2:
                    self.label_chooseR = tk.Label(self.scroll2, text="Scegli un campione del secondo vetrino:").grid(row=6,column=0)
                    self.label_chooseR1 = tk.Radiobutton(self.scroll2, text="Campione sinistro", variable=self.scelta2, value="A").grid(row=6, column=1)
                    self.label_chooseR2 = tk.Radiobutton(self.scroll2, text="Campione destro", variable=self.scelta2, value="B").grid(row=6, column=2)

                if self.img1 != None and self.img2 != None:
                    self.matchButton = tk.Button(self.scroll2, text="Confronta", command=lambda:self.check_img())
                    self.matchButton.grid(row=7, columnspan = 3, pady=7)
            else:
                if idx == 1:
                    self.label1.grid_remove()
                    self.label1 = tk.Label(self.scroll2, text="Analisi del fine non ancora eseguita")
                    self.label1.grid(row=2, column=1, sticky='w')
                else:
                    self.label2.grid_remove()
                    self.label2 = tk.Label(self.scroll2, text="Analisi del file non ancora eseguita")
                    self.label2.grid(row=4, column=1, sticky='w')

    def match(self):
        
        process = subprocess.run(["python", r"D:\Giorgio\unipi\Tirocinio\VBScript\match_pattern.py", self.img1, self.img2, self.scelta1.get(), self.scelta2.get()],
                                     capture_output=True, text=True)  
        
        if process.returncode == 0:
            output = process.stdout
            righe = output.strip().split('\n')
            bestRot = float(righe[0])
            centr1 = (int(righe[1]), int(righe[2]))
            centr2 = (int(righe[3]), int(righe[4]))
            cnt1 = json.loads(righe[5])
            cnt2 = json.loads(righe[6])
            width = int(righe[7])
            height = int(righe[8])

            contour1 = np.array(cnt1, dtype=np.int32).reshape(-1, 1, 2)
            contour2 = np.array(cnt2, dtype=np.int32).reshape(-1, 1, 2)

            self.tk.after(0, self.update_ui, contour1, contour2, bestRot, centr1, centr2, width, height)
        
        if self.matchButton is not None:
            self.matchButton.configure(state="normal")
        if self.analisys is not None:
            self.analisys.configure(state="normal")
        if self.matchSlide is not None:
            self.matchSlide.configure(state="normal")
        self.acquire.configure(state="normal")

    def update_ui(self, contour1, contour2, bestRot, centr1, centr2, width, height):
        self.drawImg(contour1, contour2, bestRot, centr1, centr2, width, height)
        frame = ttk.Frame(self.scroll2)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid(row=8, column=2)
        tk.Label(frame, text="Migliore associazione trovata", fg = "red", font=("Helvetica", 14)).grid(row=0, column=0, columnspan=2, pady=2)
        tk.Label(frame, text="Rotazione migliore:").grid(row=1, column=0, pady=2)
        tk.Label(frame, text=str(bestRot)).grid(row=1, column=1, pady=2)
        tk.Label(frame, text="X").grid(row=2, column=0)
        tk.Label(frame, text="Y").grid(row=3, column=0)

        self.defaultX = tk.StringVar()
        self.defaultY = tk.StringVar()
        x = tk.Spinbox(frame, from_=0, to=width, textvariable=self.defaultX)
        y = tk.Spinbox(frame, from_=0, to=height, textvariable=self.defaultY)
        x.grid(row=2, column=1)
        y.grid(row=3, column=1)
        tk.Label(frame, text="").grid(row=4, columnspan=2, pady = 10)
        tk.Button(frame, text="Applica", command=lambda:self.submit(x.get(), y.get(), bestRot, centr1, centr2, frame), font=("Helvetica", 12)).grid(row=5, column=0, columnspan=2)


    def submit(self, x, y, rot, centr1, centr2, frame):
        
        point = np.array([x, y], dtype=np.float32)
        rotMatrix = cv2.getRotationMatrix2D(centr1, 360 - rot, 1.0)
        rotated_point = np.dot(rotMatrix[:, :2], point - centr1) + rotMatrix[:, 2] + centr1
        final_point = rotated_point - centr1 + centr2
        tk.Label(frame, text="Corrispondenza vetrino 2:").grid(row=4, column=0, pady = 2)
        tk.Label(frame, text=f"({int(final_point[0])}, {int(final_point[1])})").grid(row=4, column=1, pady = 2)

    def check_img(self):
        
        if self.img1 is not None or self.img2 is not None:
            self.notebook.select(self.tab2)
            self.img1 = os.path.normpath(self.img1)
            self.img2 = os.path.normpath(self.img2)
            if self.matchButton is not None:
                self.matchButton.configure(state="disabled")
            if self.analisys is not None:
                self.analisys.configure(state="disabled")
            if self.matchSlide is not None:
                self.matchSlide.configure(state="disabled")
            self.acquire.configure(state="disabled")
            thread = threading.Thread(target=self.match)
            thread.start()
            
    def drawImg(self, contour1, contour2, bestRot, centr1, centr2, width, height):
        
        if hasattr(self, 'canvas_widget'):
            self.canvas_widget.destroy()
        
        contour2 = contour2 - centr2 + centr1
        
        rotMatrix = cv2.getRotationMatrix2D(centr1, bestRot, 1.0)
        new_contour = cv2.transform(contour2, rotMatrix)
        
        img = np.zeros((height, width), dtype=np.uint8)
        
        cv2.drawContours(img, [contour1], -1, 255, 7)
        cv2.drawContours(img, [new_contour], -1, 255, 7)
        coords = cv2.findNonZero(img)
        x_min = coords[:, 0, 0].min()
        y_min = coords[:, 0, 1].min()
        x_max = coords[:, 0, 0].max()
        y_max = coords[:, 0, 1].max()

        offset = max(x_max - centr1[0], centr1[0] - x_min, centr1[1] - y_min, y_max - centr1[1]) + 150 #offset usato per ridimensionare immagine
        x1 = max(0, centr1[0] - offset)
        x2 = min(img.shape[1], centr1[0] + offset)
        y1 = max(0, centr1[1] - offset)
        y2 = min(img.shape[0], centr1[1] + offset)

        img = np.zeros((height,width, 3), dtype=np.uint8)
        cv2.drawContours(img, [contour1], -1, (0, 255, 0), 7)
        cv2.drawContours(img, [new_contour], -1, (255,0,0), 7)
        img = img[y1:y2, x1:x2]

        fig, ax = plt.subplots()
        ax.axis('off')
        ax.imshow(img) 

        canvas = FigureCanvasTkAgg(fig, master=self.scroll2)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 8, columnspan=2, padx=16, pady = 16)

    def create_frame(self, parent):

        container = ttk.Frame(parent)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container)
        v_scroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scroll = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tk.update_idletasks()
        canvas.itemconfig(window_id, width=canvas.winfo_width())

        def resize_canvas(event):
            canvas.itemconfig(window_id, width=event.width)

        canvas.bind("<Configure>", resize_canvas)
        
        return scrollable_frame

    def open_file(self):
        filepath = filedialog.askopenfilename()  # Apri la finestra di dialogo per selezionare un file

        if filepath:
            try:
                img = Image.open(filepath)
                img.thumbnail((750, 750))  # Riduce mantenendo le proporzioni
            except Exception:
                tk.Label(self.scroll1, text="File non valido").grid(row=4, columnspan=2)
                return -1
            
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(self.scroll1, image=photo)
            label.grid(row=4, columnspan = 2, padx=3)
            label.image = photo
            #self.img1 = img

            actual_row = 5
            cursor.execute("SELECT * FROM Slide WHERE Filepath = %s", (filepath,))
            result = cursor.fetchall()
            
            if result:
                tk.Label(self.scroll1, text="Immagine già analizzata e dati presenti nel DB").grid(row=actual_row, columnspan=2, pady=2)
                actual_row += 1
                actual_row = self.show_info(result[0], actual_row)
            else:
                tk.Label(self.scroll1, text="Immagine non ancora analizzata").grid(row=actual_row, columnspan=2)
                actual_row += 1
                self.analisys = tk.Button(self.scroll1, command=lambda:self.start_analisys(filepath), text="Analizza")
                self.analisys.grid(row=actual_row, columnspan = 2, pady = 10)   

    def async_analisys(self, path_img):
        process = subprocess.run(["python", r"D:\Giorgio\unipi\Tirocinio\VBScript\slide_analisys.py", path_img])
        self.tk.after(0, self.update_analisys, path_img)
    
    def update_analisys(self, path_img):
        cursor.execute("SELECT * FROM Slide WHERE Filepath = %s", (path_img,))
        result = cursor.fetchall()
        
        if result:
            self.analisys.grid_forget()
            self.show_info(result[0], 6)
        else:
            tk.Label(self.scroll1, text="Qualcosa è andato storto").grid(row=5, columnspan=2)  

    def start_analisys(self, path_img):
        self.analisys.configure(state="disabled")
        if self.matchSlide is not None:
            self.matchSlide.configure(state="disabled")
        thread = threading.Thread(target=self.async_analisys, args=(path_img,))
        thread.start()
          
    def show_info(self, result, actual_row):
        
        actual_row = self.labelAndData("PATH:", result["Filepath"], actual_row)
        actual_row = self.labelAndData("NanoGPS:", "Sì" if result["NanoGPS"] == 1 else "No", actual_row)
        cursor.execute("SELECT * FROM Pattern WHERE Slide = %s", (result["Filepath"],))
        query = cursor.fetchall()
        actual_row = self.labelAndData("Numero campioni:", str(len(query)), actual_row)
        idx = 0
        for row in query:
            tk.Label(self.scroll1, text="Campione "+ str(idx + 1), font=("Helvetica", 14), fg="blue").grid(row=actual_row, columnspan = 2, pady=5)
            actual_row += 1
            actual_row = self.labelAndData("Colorato:", "Sì" if row["Colored"] == 1 else "No", actual_row)
            actual_row = self.labelAndData("X minimo:", str(row["x_min"]), actual_row)
            actual_row = self.labelAndData("Y minimo:", str(row["y_min"]), actual_row)
            actual_row = self.labelAndData("X massimo:", str(row["x_max"]), actual_row)
            actual_row = self.labelAndData("Y massimo:", str(row["y_max"]), actual_row)
            actual_row = self.labelAndData("Centroide:", "(" + str(row["x_centr"]) + ", " + str(row["y_centr"]) + ")", actual_row)
            idx += 1

        var = tk.BooleanVar()
        check = tk.Checkbutton(self.scroll1, text="Utilizza NanoGPS", variable=var)
        check.grid(row = actual_row, columnspan=2)
        if result["NanoGPS"] == 0:
            check.configure(state="disabled")
        actual_row += 1

        self.analisys = tk.Button(self.scroll1, command=lambda:self.start_analisys(result["Filepath"]), text="Analizza")
        self.analisys.grid(row=actual_row, column = 0, pady = 10)
        self.analisys.configure(state="normal")
        self.matchSlide = tk.Button(self.scroll1, command=lambda:self.start_slide_match(result["ContourPath"]), text="Match campioni")
        self.matchSlide.grid(row=actual_row, column = 1, pady = 10)
        self.matchSlide.configure(state="normal")
        if(len(query)!=2):
            self.matchSlide.configure(state="disabled")

        return actual_row
    
    def start_slide_match(self, path_img):
        self.img1 = path_img
        self.img2 = path_img
        self.scelta2.set("B")
        print(self.img1, self.img2)
        self.check_img()
    
    def labelAndData(self, label, data, actual_row):
        tk.Label(self.scroll1, text=label).grid(row=actual_row, column=0, pady=2)
        tk.Label(self.scroll1, text=data).grid(row=actual_row, column=1, pady=2)
        actual_row += 1
        return actual_row
    
window = tkinter()

window.tk.mainloop()