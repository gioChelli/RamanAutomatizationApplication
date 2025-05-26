import sys
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk

#parametri di dove sono iniziate le scansioni delle immagini, per rendere algoritmo generale ho due scelte:
# -chiederli in input all'utente
# -leggere da file system il nome delle foto
ROW_NOTCOLORED = 25000 
COLUMN_NOTCOLORED = 14630
ROW_COLORED = 22360
COLUMN_COLORED = 34290

class tkinter:
    def __init__(self, centr1, centr2, bestMatr):
        self.tk = tk.Tk()
        self.centr1 = centr1
        self.centr2 = centr2
        self.matrix = bestMatr
        self.tk.geometry("400x400")
        self.tk.title("Ottieni Coordinate")
        welcome_label = tk.Label(self.tk,
                         text="Inserisci coordinate immagine colorata",
                         fg = "red",
                         font=("Helvetica", 15))
        welcome_label.grid(row=0, columnspan=2)
        self.home()
    
    def home(self):
        tk.Label(self.tk, text="X").grid(row=1)
        tk.Label(self.tk, text="Y").grid(row=2)

        x = tk.Entry(self.tk)
        y = tk.Entry(self.tk)

        x.grid(row=1, column=1)
        y.grid(row=2, column=1)
        tk.Label(self.tk, text="").grid(row=3, pady=10)
        self.button = tk.Button(text="Conferma", command=lambda:self.submit(x, y), font=("Helvetica", 12)).grid(row=4, columnspan=2)

    def submit(self, x, y):
        
        tk.Label(self.tk, text="").grid(row=5, pady=10)
        try:
            centr_x = int(x.get()) - ROW_COLORED
            centr_y = int(y.get()) - COLUMN_COLORED
        except:
            tk.Label(self.tk, text="Inserisci numeri interi").grid(row=6, columnspan=2)
            return
        
        print(centr_x, centr_y)
        
        R = self.matrix[:, :2]
        p = np.array([centr_x, centr_y])
        p_rel = p - self.centr2
        p_rot = R @ p_rel
        out = p_rot + self.centr1 
        out[0] += ROW_NOTCOLORED
        out[1] += COLUMN_NOTCOLORED

        tk.Label(self.tk, text=f"Corrispondente:({out[0]:.0f}, {out[1]:.0f})").grid(row=6, columnspan=2)

#R = rotMatrix[:, :2]
#t = rotMatrix[:, 2]

# punto relativo al centroide
#p_relative = p - centroid_src
# ruoto
#p_rotated = R @ p_relative
# sposto rispetto al secondo centroide
#p_transformed = p_rotated + centroid_dst


def main(img1_name, img2_name): #i due argomenti sono le immagini dei vetrini

    #img1_name = "acqBianco2_unita.jpg"  
    #img2_name = "acqColorato1_unita.jpg"    
    
    img1 = cv2.imread(img1_name, cv2.IMREAD_COLOR)
    img2 = cv2.imread(img2_name, cv2.IMREAD_COLOR)

    result = onlyPurple(img2) #ottengo l'immagine 2 con colore più scuro, per evitare rumore

    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)    
    img2_gray = cv2.cvtColor(result, cv2.COLOR_HSV2BGR) 
    img2_gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

    matrix1 = np.ones(img1_gray.shape, dtype="uint8") * 70 # matrice usata per schiarire e quindi rimuovere rumore delle righe foto
    matrix3 = np.ones(img2_gray.shape) * 1.3 #matrice per + contrasto
    
    img1_gray = cv2.add(img1_gray, matrix1)  #schiarisco la figura non colorata perche piu scura e con maggior rumore
    img2_gray = np.uint8(np.clip(cv2.multiply(np.float64(img2_gray), matrix3), 0, 255)) #aumento il contrasto delle immagini
    img1_gray = np.uint8(np.clip(cv2.multiply(np.float64(img1_gray), matrix3), 0, 255))

    #bitmap adattiva, figura bianca e sfondo nero
    img1_gray = cv2.adaptiveThreshold(img1_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 3) 
    img2_gray = cv2.adaptiveThreshold(img2_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 3)

    #allargo dimensioni immagini per la rotazione
    dimX = img1.shape[0] + img1.shape[0]//2
    dimY = img1.shape[1] + img1.shape[1]//2
    canvas1 = np.zeros((dimX, dimY), dtype=np.uint8)
    canvas1[img1_gray.shape[0]//4:img1_gray.shape[0]//4*5, img1_gray.shape[1]//4:img1_gray.shape[1]//4*5] = img1_gray
    canvas2 = np.zeros((dimX, dimY), dtype=np.uint8)
    canvas2[img2_gray.shape[0]//4:img2_gray.shape[0]//4*5, img2_gray.shape[1]//4:img2_gray.shape[1]//4*5] = img2_gray

    #filtro dove elimino un po di rumore nei contorni frastagliati
    canvas1 = cv2.bilateralFilter(canvas1, 30, 75, 75)  
    canvas2 = cv2.bilateralFilter(canvas2, 30, 75, 75) 

    #codice fondamentale, se per futuri esempi non funziona probabilmente cambiare questi parametri
    density = cv2.blur(canvas2.astype(np.float32), (47, 47)) / 255
    mask = (density > 0.000005).astype(np.uint8) * 255
    new_img2 = np.maximum(canvas2, mask.astype(np.uint8))

    #plt.figure(figsize=[15,8])
    #plt.subplot(121); plt.axis('on'); plt.imshow(img1_gray, cmap="gray"); plt.title("Not colored")
    #plt.subplot(122); plt.axis('on'); plt.imshow(new_img2, cmap="gray"); plt.title("Colored")
    
    #plt.show()

    #ottengo i contorni    
    contours1, _ = cv2.findContours(canvas1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)   
    contours2, _ = cv2.findContours(new_img2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    img1 = np.zeros(canvas1.shape, dtype=np.uint8)
    img2 = np.zeros(new_img2.shape, dtype=np.uint8)

    filter_contours1 = []
    for i in contours1:
        if(len(i) > 3000):
            filter_contours1.append(i)

    filter_contours2 = []
    for i in contours2:
        if(len(i) > 3000):
            filter_contours2.append(i)

    img1 = np.zeros(img1.shape, dtype=np.uint8)
    img2 = np.zeros(img2.shape, dtype=np.uint8) 
    cv2.drawContours(img2, filter_contours2, -1, 255, 3)
    cv2.drawContours(img1, filter_contours1, -1, 255, 3)

    #print(len(filter_contours2))

    #plt.figure(figsize=[15,8])
    #plt.subplot(121); plt.axis('on'); plt.imshow(img1, cmap="gray"); plt.title("Not colored")
    #plt.subplot(122); plt.axis('on'); plt.imshow(img2, cmap="gray"); plt.title("Colored")
    
    #plt.show()
   
    M1 = cv2.moments(filter_contours1[0])

    cx1 = int(M1["m10"] / M1["m00"])  # coordinata X del centro
    cy1 = int(M1["m01"] / M1["m00"])  # coordinata Y del centro
    centroide1 = np.array([cx1, cy1])
    
    M2 = cv2.moments(filter_contours2[0])

    cx2 = int(M2["m10"] / M2["m00"])  # coordinata X del centro
    cy2 = int(M2["m01"] / M2["m00"])  # coordinata Y del centro
    centroide2 = np.array([cx2, cy2])

    print(cx1, cx2)
    print(cy1, cy2)

    i = 0
    resTot = 0
    resBest = 1
    best_matrix = None
    best_contours = None

    while i < 360:
        
        rotMatrix = cv2.getRotationMatrix2D((cx2, cy2), i, 1.0)
        resTot = 0
        rotated_contours = [cv2.transform(cnt, rotMatrix) for cnt in filter_contours2]
        
        for f in rotated_contours:
            resTot =  cv2.matchShapes(filter_contours1[0], f, cv2.CONTOURS_MATCH_I2, 0.0) 
            
            if(resTot < resBest):
                best_contours = rotated_contours
                resBest = resTot
                best_matrix = rotMatrix
            
        i = i + 1

    print(resBest)
    
    img2 = np.zeros(img2.shape, dtype=np.uint8)
    cv2.drawContours(img2, best_contours, -1, 255, 3)

    cv2.circle(img1, (cx1, cy1), radius=30, color=255, thickness=-1)
    cv2.circle(img2, (cx2, cy2), radius=30, color=255, thickness=-1)
    
    plt.figure(figsize=[15,8])
    plt.subplot(121); plt.axis('on'); plt.imshow(img1, cmap="gray"); plt.title("Not colored")
    plt.subplot(122); plt.axis('on'); plt.imshow(img2, cmap="gray"); plt.title("Colored")

    window = tkinter(centroide1, centroide2, best_matrix)
    
    #plt.show()
    window.tk.mainloop()

    return

def onlyPurple(img2):

    hsv = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
    lower_purple = np.array([125, 5, 5], dtype=np.uint8)
    upper_purple = np.array([160, 255, 255], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower_purple, upper_purple)

    white_background = np.full(img2.shape, 255, dtype=np.uint8)
    purple_background = np.full(img2.shape,  np.array([140, 80, 80], dtype=np.uint8), dtype=np.uint8)

    # Applica maschera: dove è True, mantieni il colore viola, altrimenti bianco
    result = np.where(mask[:, :, np.newaxis] == 255, purple_background, white_background)

    return result

if len(sys.argv) == 3:
    main(sys.argv[1], sys.argv[2])
else:
    print("Use:", sys.argv[0], "img_notColored", "img_Colored")