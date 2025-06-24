from enum import Enum
import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys
from scipy.spatial.distance import cdist
import os.path
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",      
    user="root",
    password="Giocondo2021$",
    database="Raman_DB"
)

cursor = conn.cursor()

WHITE_COLOR = 255
#questi sono tutti valori in pixel
PATTERN_FRAGMENT_MIN_DIMENSION = 100000 #dimensione minima dei frammenti che ci interessano, tutto cio che e piu piccolo puo essere polvere o comunque come affermato dagli istologi irrilevante
FRAGMENT_MAX_DISTANCE = 1000 #campo che prendo in considerazione intorno a un pattern, in cui ci potrebbero essere frammenti interessanti
LINE_BOUND = 0.005 #questo valore viene indicato come soglia della proporzione area/perimetro di un contorno sotto la quale significa che abbiamo rilevato un contorno che non è altro che una linea retta, ovvero il bordo del coprivetrino
NANOGPS_AREA = 10000000 #il NanoGPS viene fissato al vetrino con dello scotch, che andrà a prendere un area molto vasta del vetrino, sicuramente almeno magggiore di questa soglia
PATTERN_MINIMUM_AREA = 2000000 #minima dimensione dell'area di un campione significativo

class GlassType(Enum):
    TWO_COLORED = 0
    TWO_WHITE = 1
    ONE_COLORED = 2
    ONE_WHITE = 3
    ONE_BOTH = 4
    EMPTY = 5

def onlyPurple(img):

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #qui vado a stabilire quali sono i colori che voglio intercettare nella maschera in formato hsv
    #in questo caso indico colori dal rosa chiaro a quello piu scuro che sono i colori dei vetrini colorati
    lower_purple = np.array([125, 85, 85], dtype=np.uint8)
    upper_purple = np.array([160, 255, 255], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower_purple, upper_purple)

    #qui definisco i colori da assegnare ai pixel nel caso in cui soddisfano i requisiti della maschera oppure no
    #il primo definsce il bianco, ils secondo un viola abbastanza scuro per riconscerlo facilmente
    white_background = np.full(img.shape, (0,0,255), dtype=np.uint8)
    purple_background = np.full(img.shape,  np.array([140, 80, 80], dtype=np.uint8), dtype=np.uint8)

    # Applica maschera: dove è True, mantieni il colore viola, altrimenti bianco
    result = np.where(mask[:, :, np.newaxis] == 255, purple_background, white_background)

    result = cv2.cvtColor(result, cv2.COLOR_HSV2BGR) 

    return result

def main(path_img):

    glass = GlassType.EMPTY
    img = cv2.imread(path_img, cv2.IMREAD_COLOR)
    if img is None:
        return -1
    
    #plt.figure(figsize=[15,8])
    #plt.subplot(); plt.axis('on'); plt.imshow(img, cmap="gray"); plt.title("Not colored")
    #plt.show()
    
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #applico bitmap e un po di filtri per definire meglio i contorni
    _, bitmapImg = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY_INV)
    bitmapImg = cv2.blur(bitmapImg, (17,17)) #applico filtro per sfocatura su un campo di 17 pixel
    bitmapImg = cv2.bilateralFilter(bitmapImg, 30, 75, 75)  #img, pixel considerati, considerazione diverse intensità di colore, considerare distanza
    #ricerca dei contorni
    contours, _ = cv2.findContours(bitmapImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    img_gray = None
    nanoGPS = False
    xNano = yNano = wNano = hNano = None
    filter_contours_gray= []

    #filtro i contorni andando a cercare prima di tutto il NanoGPS se presente, che avra una forma rettangolare
    #dopo controllo le dimensioni dei contorni trovati di dimensione rilevante che saranno i campioni, escludendo 
    #quelli con dimensione troppo elevata che corrisponderanno alle linee del vetrino
    for i in contours:
        epsilon = 0.02 * cv2.arcLength(i, True)
        approx = cv2.approxPolyDP(i, epsilon, True)
        perimeter = cv2.arcLength(i, closed=True)
        area = cv2.contourArea(i)
        comp = area / (perimeter * perimeter)

        if comp < LINE_BOUND: #soglia bassa che indica che abbiamo rilevato le linee del coprivetrino
            continue
        elif len(approx)== 4 and cv2.isContourConvex(approx) and not nanoGPS and area > NANOGPS_AREA:
            print(area)
            nanoGPS = True
            (xNano,yNano,wNano,hNano) = cv2.boundingRect(approx)
        elif area > PATTERN_MINIMUM_AREA:
            filter_contours_gray.append(i)

    prova =  np.zeros(bitmapImg.shape, dtype=np.uint8)
    prova = cv2.drawContours(prova, filter_contours_gray, -1, 255, -1)
    #plt.figure(figsize=[15,8])
    #plt.subplot(); plt.axis('on'); plt.imshow(prova, cmap="gray"); plt.title("Not colored")
    #plt.show()
    
    if not nanoGPS:
        print("NanoGPS non presente")
    else:
        print("NanoGPS presente")
    
    print(len(filter_contours_gray)) 

    #ottengo la maschera per individuare vetrini colorati
    result = onlyPurple(img) 
    result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    colored_contour = None
    
    filter_contours = []
    #controllo se c'è campione colorato
    if not np.mean(result) >= WHITE_COLOR: 
        
        _, bitmapImgCol = cv2.threshold(result, 127, 255, cv2.THRESH_BINARY_INV)
        contoursColored, _ = cv2.findContours(bitmapImgCol, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i in contoursColored:
            area = cv2.contourArea(i)
            if area > PATTERN_MINIMUM_AREA:
                filter_contours.append(i)
        
        final_contours = [[] for _ in filter_contours]
        idx = 0
        for i in contoursColored:
            idx = 0
            for j in filter_contours:
                if contour_distance(i, j) < FRAGMENT_MAX_DISTANCE:
                    final_contours[idx].append(i)
                    break
                idx += 1

        final_img = [[] for _ in final_contours]
        idx = 0
        for i in final_contours:
            final_img[idx] = np.zeros(bitmapImgCol.shape, dtype=np.uint8)
            final_img[idx] = cv2.drawContours(final_img[idx], i, -1, 255, -1)
            idx += 1

        for idx in range(len(final_contours)):
            while len(final_contours[idx]) > 1:
                
                square = (13, 13) #area considerata per filtrare i pixel
                final_img[idx] = define_contour(final_img[idx], square)
                #plt.figure(figsize=[15,8])
                #plt.subplot(); plt.axis('on'); plt.imshow(final_img[idx], cmap="gray"); plt.title("Not colored")
                #plt.show()
                contours, _ = cv2.findContours(final_img[idx], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                filter_contours = []
                for i in contours:
                    area = cv2.contourArea(i)
                    if area > PATTERN_FRAGMENT_MIN_DIMENSION:
                        filter_contours.append(i)
                
                if len(filter_contours) == 0:
                    print("Contorni troppo poco definiti")
                    return -1
                final_contours[idx] = filter_contours 

        print(len(final_contours))        
        if len(final_contours)==2:
            glass = GlassType.TWO_COLORED
            filter_contours_gray = []
            filter_contours_gray.append(final_contours[0][0])
            filter_contours_gray.append(final_contours[1][0])
        elif len(final_contours)==1:
            glass = GlassType.ONE_COLORED
            colored_contour = final_contours[0][0][:, 0, 0].min()
        elif len(final_contours) > 2:
            print("Errore nella rilevazione degli oggetti")
            return -1
        bitmapImgCol = None

    result = None
    left = False
    
    #in base ai risultati definisco il tipo di vetrino che ho trovato
    if len(filter_contours_gray) == 2 and glass == "ONE COLORED":
        glass = GlassType.ONE_BOTH
        x_min1 = filter_contours_gray[0][:, 0, 0].min()
        x_min2 = filter_contours_gray[1][:, 0, 0].min()
        if (x_min1 - colored_contour) < (x_min2 - colored_contour):
            left = True
            filter_contours_gray[0] = final_contours[0]
        else:
            filter_contours_gray[1] = final_contours[0]
    elif len(filter_contours_gray) == 2 and glass == "EMPTY":
        glass = GlassType.TWO_WHITE
    elif len(filter_contours_gray) == 1 and glass == "EMPTY":
        glass = GlassType.ONE_WHITE
    elif len(filter_contours_gray) > 2:
        print("Errore nella rilevazione dei contorni, rumore troppo elevato")
        return -1
    elif len(filter_contours_gray) == 0:
        print("Vetrino vuoto o campione troppo frammentato")
        return 0 

    #aggiungo ai contorni dei campioni(ovvero quelli piu grandi) altri contorni a loro vicini che potrebbero
    #sempre fare parte del campione ma essere leggermente staccati per via del taglio oppure fattori di rumore

    img = np.zeros(img.shape, dtype=np.uint8)
    approx_contours = []
    centr = []
    for idx in range(len(filter_contours_gray)):
        approx_contours.append(cv2.approxPolyDP(filter_contours_gray[idx], 5, True))
        centr.append(compute_center([approx_contours[idx]]))
        img = cv2.drawContours(img, filter_contours_gray[idx], -1, 255, 7)
    
    final_img = [[] for _ in filter_contours_gray]
    idx = 0
    for i in filter_contours_gray:
        final_img[idx] = np.zeros(bitmapImg.shape, dtype=np.uint8)
        final_img[idx] = cv2.drawContours(final_img[idx], i, -1, 255, -1)
        idx += 1
    #plt.figure(figsize=[15,8])
    #plt.subplot(); plt.axis('on'); plt.imshow(img, cmap="gray"); plt.title("Not colored")
    #plt.show()

    parent_folder = os.path.dirname(path_img)
    basename = os.path.basename(path_img)
    name = os.path.splitext(basename)[0] + "_contour.jpg"
    new_path = os.path.join(parent_folder, name)
    cv2.imwrite(new_path, img)

    if len(approx_contours) == 2:
        x_min1 = approx_contours[0][:, 0, 0].min()
        x_min2 = approx_contours[1][:, 0, 0].min()

    if nanoGPS:
            cursor.execute("""
                INSERT INTO Slide(Filepath, NanoGPS, x_nano, y_nano, ContourPath)
                        VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE NanoGPS = VALUES(NanoGPS), x_nano = VALUES(x_nano), y_nano = VALUES(y_nano), ContourPath = VALUES(ContourPath)
                       """, (path_img, nanoGPS, float(xNano), float(yNano), new_path))
    else: 
        cursor.execute("""
            INSERT INTO Slide(Filepath, NanoGPS, ContourPath)
                    VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE NanoGPS = VALUES(NanoGPS), ContourPath = VALUES(ContourPath)
                       """, (path_img, nanoGPS, new_path))

    cursor.execute("""
                DELETE FROM Pattern WHERE Slide = %s
                       """, (path_img,))
    
    for idx in range(len(final_img)):
        coords = cv2.findNonZero(final_img[idx])
        center = tuple(map(int, centr[idx]))
        x_min = coords[:, 0, 0].min()
        y_min = coords[:, 0, 1].min()
        x_max = coords[:, 0, 0].max()
        y_max = coords[:, 0, 1].max()
        colored = False
        if glass == GlassType.TWO_COLORED or glass == GlassType.ONE_COLORED:
            colored = True
        elif glass == GlassType.ONE_BOTH:
            if ((x_min == x_min1 and x_min1 < x_min2 and left) or
                (x_min == x_min2 and x_min2 < x_min1 and left) or
                (x_min == x_min1 and x_min1 > x_min2 and not left) or
                (x_min == x_min2 and x_min2 > x_min1 and not left)):
                colored = True
        print("inserisco")
        
        cursor.execute("""
                INSERT INTO Pattern(Slide, x_min, y_min, x_max, y_max, x_centr, y_centr, Colored)
                        VALUES ( %s,  %s, %s, %s, %s, %s, %s, %s)
                       """, (path_img, float(x_min), float(y_min), float(x_max), float(y_max), float(center[0]), float(center[1]), colored))
    
    conn.commit()
    cursor.close()
    conn.close()

    #plt.figure(figsize=[15,8])
    #plt.subplot(121); plt.axis('on'); plt.imshow(final_img[0], cmap="gray"); plt.title("Not colored")
    #plt.subplot(122); plt.axis('on'); plt.imshow(final_img[1], cmap="gray"); plt.title("Colored")
    #plt.show()
    
    #if(glass == GlassType.ONE_BOTH or glass == GlassType.TWO_COLORED or glass == GlassType.TWO_WHITE):
        #search_distance(final_contours, final_img)
        #search_distance_hull(final_contours, final_img)

    return

def define_contour(img, square):
    density = cv2.blur(img.astype(np.float32), square) / 255
    mask = (density > 0.000005).astype(np.uint8) * 255
    new_img = np.maximum(img, mask.astype(np.uint8))
    #print(square[0])
    return new_img
    
def contour_distance(c1, c2):
    d = cdist(c1.reshape(-1, 2), c2.reshape(-1, 2))
    return d.min()

#trova il centroide usando la media pesata dei centroidi dei diversi contour
def compute_center(contour):
    
    M = []
    for i in contour:
        M.append(cv2.moments(i))

    cx_total = 0
    cy_total = 0
    area_total = 0
    
    for m in M:
        if m["m00"] != 0:
            cx = m["m10"] / m["m00"]
            cy = m["m01"] / m["m00"]
            cx_total += cx * m["m00"]
            cy_total += cy * m["m00"]
            area_total += m["m00"]
    
    if area_total > 0:
        cx_avg = cx_total / area_total
        cy_avg = cy_total / area_total
    
    centr = np.array([cx_avg, cy_avg])
    centr = tuple(centr.astype(int))

    return centr

if len(sys.argv) == 2:
    main(sys.argv[1])
else:
    print("Uso:", sys.argv[0], "nome_directory")