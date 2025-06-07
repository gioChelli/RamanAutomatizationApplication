import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, ttk

#parametri di dove sono iniziate le scansioni delle immagini, per rendere algoritmo generale ho due scelte:
# -chiederli in input all'utente
# -leggere da file system il nome delle foto
ROW_NOTCOLORED = 25000 
COLUMN_NOTCOLORED = 14630
ROW_COLORED = 22360
COLUMN_COLORED = 34290

class tkinter:
    def __init__(self):
        self.tk = tk.Tk()
        self.tk.geometry("800x800")
        self.tk.title("Matching campioni")

        self.notebook = ttk.Notebook(self.tk)
        self.notebook.pack(expand=True, fill='both')

        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab1.grid_columnconfigure(0, weight=1)
        self.tab1.grid_columnconfigure(1, weight=1)
        self.tab2.grid_columnconfigure(0, weight=1)
        self.tab2.grid_columnconfigure(1, weight=1)
        self.tab1.grid_propagate(False)
        self.tab2.grid_propagate(False)

        # Aggiungi schede al notebook
        self.notebook.add(self.tab1, text='Seleziona campioni')
        self.notebook.add(self.tab2, text='Matching campioni')

        self.img1 = None
        self.img2 = None
        tk.Label(self.tab1, text="Seleziona campioni da confrontare", fg = "red", font=("Helvetica", 16)).grid(row=1, columnspan=2)

        tk.Label(self.tab1, text="").grid(row=4, pady=4)
        tk.Button(self.tab1, text="Scegli campione 1", command=lambda:self.open_file(1)).grid(row=2, column = 0)
        tk.Label(self.tab1, text="Nessun Path selezionato al momento", anchor='w').grid(row=2, column=1, sticky='w')
        tk.Label(self.tab1, text="").grid(row=3, pady=4)
        tk.Button(self.tab1, text="Scegli campione 2", command=lambda:self.open_file(2)).grid(row=4, column = 0)
        tk.Label(self.tab1, text="Nessun Path selezionato al momento", anchor='w').grid(row=4, column=1, sticky='w')
        tk.Label(self.tab1, text="").grid(row=5, pady=4)
        tk.Button(self.tab1, text="Confronta", command=lambda:self.check_img(self.img1, self.img2)).grid(row=6, columnspan = 2)

    def check_img(self, img1, img2):
        if img1 is not None or img2 is not None:
            self.notebook.select(self.tab2)
            main(self.img1, self.img2)
        else:
            tk.Label(self.tab1, text="Immagini scelte non valide").grid(row=4, columnspan=2)

    def open_file(self, index):
        filepath = filedialog.askopenfilename()  # Apri la finestra di dialogo per selezionare un file

        if filepath:
        
            img = cv2.imread(filepath, cv2.IMREAD_COLOR)
            if img is None:
                tk.Label(self.tab1, text="File non valido").grid(row=4, columnspan=2)
                return -1
            
            if index == 1:
                tk.Label(self.tab1, text=filepath, anchor='w').grid(row=2, column = 1, padx=3, sticky='w')
                self.img1 = img
            elif index == 2:
                tk.Label(self.tab1, text=filepath, anchor='w').grid(row=4, column = 1, padx=3, sticky='w')
                self.img2 = img
                        
       
    def home(self, centr1, centr2, rot, shape, contour1, contour2):
        self.centroide = np.array(centr1).copy() #questo è il centroide che vado a usare per le traslazioni
        self.centr1 = centr1 #questo è il centroide della prima immagine
        self.centr2 = centr2 #questo è il centroide della seconda immagine
        self.bestRot = rot #questo è il grado di rotazione migliore calcolato dal sistema
        self.myRot = rot #rotazione usata per modificare a piacimento dell'utente
        self.shape = shape #dimensioni dell'immagine
        self.contour1 = contour1 #il contorno della prima immagine
        self.contour2 = contour2 #il contorno della seconda immagine
        welcome_label = tk.Label(self.tab2,
                         text="Inserisci coordinate immagine colorata",
                         fg = "red",
                         font=("Helvetica", 16))
        welcome_label.grid(row=0, columnspan=2)
        tk.Label(self.tab2, text="X", font=("Helvetica", 12)).grid(row=1, column=0)
        tk.Label(self.tab2, text="Y", font=("Helvetica", 12)).grid(row=2, column=0)
        tk.Label(self.tab2, text="Rotazione",font=("Helvetica", 12)).grid(row=3, column=0)

        self.defaultX = tk.StringVar()
        self.defaultY = tk.StringVar()
        self.defaultX.set(self.centr1[0] + ROW_COLORED)
        self.defaultY.set(self.centr1[1] + COLUMN_COLORED)
        self.defaultRot = tk.StringVar()
        self.defaultRot.set(self.bestRot)

        x = tk.Spinbox(self.tab2, from_=ROW_COLORED, to=ROW_COLORED + self.shape[0], textvariable=self.defaultX)
        y = tk.Spinbox(self.tab2, from_=COLUMN_COLORED, to=COLUMN_COLORED + self.shape[1], textvariable=self.defaultY)
        rot = tk.Spinbox(self.tab2, from_=0, to=359, textvariable=self.defaultRot)

        x.grid(row=1, column=1)
        y.grid(row=2, column=1)
        rot.grid(row = 3, column=1)
        tk.Label(self.tab2, text="").grid(row=4, pady=2)
        
        tk.Button(self.tab2, text="Applica", command=lambda:self.submit(x, y, rot), font=("Helvetica", 12)).grid(row=5, columnspan=2)
        tk.Label(self.tab2, text="").grid(row=6, pady=4)
        tk.Button(self.tab2, text="Posizioni su vetrino", command=lambda:self.original_position(), font=("Helvetica", 12)).grid(row=9, column=0)
        tk.Button(self.tab2, text="Posizione iniziale", command=lambda:self.best_position(), font=("Helvetica", 12)).grid(row=9, column=1)
        tk.Label(self.tab2, text="").grid(row=8, pady=5)
        self.drawImg()

    def original_position(self):
        self.centroide = np.array(self.centr2).copy()
        self.myRot = self.bestRot
        self.defaultX.set(self.centr2[0] + ROW_COLORED)
        self.defaultY.set(self.centr2[1] + COLUMN_COLORED)
        self.defaultRot.set(self.bestRot)
        self.drawImg()

    def best_position(self):
        
        self.centroide = np.array(self.centr1).copy()
        self.myRot = self.bestRot
        self.defaultX.set(self.centr1[0] + ROW_COLORED)
        self.defaultY.set(self.centr1[1] + COLUMN_COLORED)
        self.defaultRot.set(self.bestRot)
        self.drawImg()
        

    def drawImg(self):
        
        if hasattr(self, 'canvas_widget'):
            self.canvas_widget.destroy()
        
        center = (float(self.centroide[0]), float(self.centroide[1]))
        rotMatrix = cv2.getRotationMatrix2D(center, self.myRot, 1.0)
        new_contour2 = cv2.transform(self.contour2[0], rotMatrix)
        new_cont2 = new_contour2 + np.array([[[self.centroide[0], self.centroide[1]]]]) - np.array([[[self.centr2[0], self.centr2[1]]]])
        
        img = np.zeros((self.shape[0],self.shape[1],3), dtype=np.uint8)
        
        cv2.drawContours(img, self.contour1, -1, (0,255,0), 7)
        cv2.drawContours(img, [new_cont2], -1, (255,0,0), 7)
        fig, ax = plt.subplots()
        ax.axis('off')
        ax.imshow(img) 

        canvas = FigureCanvasTkAgg(fig, master=self.tab2)
        canvas.draw()
        canvas.get_tk_widget().grid(row = 7, columnspan=2, padx=10)

    def submit(self, x, y, rot):
        
        #tk.Label(self.tk, text="").grid(row=5, pady=10)
        try:
            self.centroide[0] = float(x.get()) - ROW_COLORED
            self.centroide[1] = float(y.get()) - COLUMN_COLORED
            self.myRot = float(rot.get())

            self.drawImg()
        
            #R = self.matrix[:, :2]
            #p = np.array([centr_x, centr_y])
            #p_rel = p - self.centr2
            #p_rot = R.T @ p_rel #trasposta perché faccio rotazione inversa
            #out = p_rot + self.centr1 
            #out[0] += ROW_NOTCOLORED
            #out[1] += COLUMN_NOTCOLORED

            #tk.Label(self.tk, text=f"Corrispondente:({out[0]:.0f}, {out[1]:.0f})").grid(row=6, columnspan=2)
        except:
            tk.Label(self.tab2, text="Valori inseriti non validi").grid(row=8, columnspan=2)
            
        return
    
def filter_image(img):
    imgWhite = False
    
    result = onlyPurple(img) 
    if not np.mean(result) > 254: #controllo se era un campione non colorato non faccio nulla
        img = result
    else:
        imgWhite = True

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  
    
    if(imgWhite):
        matrix1 = np.ones(img_gray.shape, dtype="uint8") * 70 # matrice usata per schiarire e quindi rimuovere rumore delle righe foto
        img_gray = cv2.add(img_gray, matrix1)  #schiarisco la figura non colorata perche piu scura e con maggior rumore

    #aumento il contrasto delle immagini
    matrix2 = np.ones(img_gray.shape) * 1.3 #matrice per + contrasto
    img_gray = np.uint8(np.clip(cv2.multiply(np.float64(img_gray), matrix2), 0, 255))
    
    #rendo l'immagine una bitmap
    img_gray = cv2.adaptiveThreshold(img_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 3) 

    #allargo dimensioni immagini per la rotazione di 1/2 rispetto alla loro dimensione e disegno al centro
    dimX = img.shape[0] + img.shape[0]//2
    dimY = img.shape[1] + img.shape[1]//2
    canvas = np.zeros((dimX, dimY), dtype=np.uint8)
    canvas[img_gray.shape[0]//4:img_gray.shape[0]//4*5, img_gray.shape[1]//4:img_gray.shape[1]//4*5] = img_gray
    
    #filtro dove elimino un po di rumore nei contorni frastagliati
    canvas = cv2.bilateralFilter(canvas, 30, 75, 75)  
    
    return canvas
    
def define_contour(img, square):
    density = cv2.blur(img.astype(np.float32), square) / 255
    mask = (density > 0.000005).astype(np.uint8) * 255
    new_img = np.maximum(img, mask.astype(np.uint8))
    #print(square[0])
    return new_img
    

def find_contour(img):
    #ottengo i contorni 
    while True:  
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        filter_contours = []
        for i in contours:
            if(len(i) > 2000):
                filter_contours.append(i)

        if(len(filter_contours) == 1):
            break
        elif len(filter_contours) == 0:
            print("Contorni troppo poco definiti")
            return -1
        else:
            square = (27, 27) #area considerata per filtrare i pixel
            img = define_contour(img, square)
        
    return filter_contours

def main(img1, img2): #i due argomenti sono le immagini dei vetrini 
    
    #filtro le immagini
    img1 = filter_image(img1)
    img2 = filter_image(img2)

    filter_contours1 = find_contour(img1)
    filter_contours2 = find_contour(img2)

    if(filter_contours1 == -1 or filter_contours2 == -1):
        return -1
   
    M1 = cv2.moments(filter_contours1[0])

    cx1 = int(M1["m10"] / M1["m00"])  # coordinata X del centro
    cy1 = int(M1["m01"] / M1["m00"])  # coordinata Y del centro
    centroide1 = np.array([cx1, cy1])
    
    M2 = cv2.moments(filter_contours2[0])

    cx2 = int(M2["m10"] / M2["m00"])  # coordinata X del centro
    cy2 = int(M2["m01"] / M2["m00"])  # coordinata Y del centro
    centroide2 = np.array([cx2, cy2])

    #print(cx1, cx2)
    #print(cy1, cy2)

    i = 0
    resBest = 100

    approx_contours1 = cv2.approxPolyDP(filter_contours1[0], 10, True)
    approx_contours2 =  cv2.approxPolyDP(filter_contours2[0], 10, True)

    approx_contours2 = approx_contours2 + np.array([[[cx1, cy1]]]) - np.array([[[cx2, cy2]]])

    bestRot = 0
    sc = cv2.createShapeContextDistanceExtractor()
    while i < 360:
        
        rotMatrix = cv2.getRotationMatrix2D((cx2, cy2), i, 1.0)
        rotated_contours = cv2.transform(approx_contours2, rotMatrix)
        
        distance = sc.computeDistance(approx_contours1, rotated_contours)
        
        if(distance < resBest):
            resBest = distance
            bestRot = i
        print(i, distance)
        i = i + 1

    #print(resBest)
    #print(cx1, cy1)
    
    
    #img1 = np.zeros(img1.shape, dtype=np.uint8)
    #img2 = np.zeros(img2.shape, dtype=np.uint8) 
    #cv2.drawContours(img1, filter_contours1, -1, 255, 3)
    #cv2.drawContours(img1, filter_contours2, -1, 255, 3)

    #cv2.circle(img1, (cx1, cy1), radius=30, color=255, thickness=-1)
    #cv2.circle(img2, (cx2, cy2), radius=30, color=255, thickness=-1)
    
    #plt.figure(figsize=[15,8])
    #plt.subplot(121); plt.axis('on'); plt.imshow(img1, cmap="gray"); plt.title("Not colored")
    #plt.subplot(122); plt.axis('on'); plt.imshow(img2, cmap="gray"); plt.title("Colored")

    window.home(centroide1, centroide2, bestRot, img1.shape, filter_contours1, filter_contours2)
    
    #plt.show()

    return

def onlyPurple(img):

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_purple = np.array([125, 85, 85], dtype=np.uint8)
    upper_purple = np.array([160, 255, 255], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower_purple, upper_purple)

    white_background = np.full(img.shape, (0,0,255), dtype=np.uint8)
    purple_background = np.full(img.shape,  np.array([140, 80, 80], dtype=np.uint8), dtype=np.uint8)

    # Applica maschera: dove è True, mantieni il colore viola, altrimenti bianco
    result = np.where(mask[:, :, np.newaxis] == 255, purple_background, white_background)

    result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR) 

    return result

window = tkinter()

window.tk.mainloop()