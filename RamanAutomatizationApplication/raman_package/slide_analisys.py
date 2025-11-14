from enum import Enum
import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
import os.path
import shutil
import mysql.connector
import json

LINE_BOUND = 0.005 #questo valore viene indicato come soglia della proporzione area/perimetro di un contorno sotto la quale significa che abbiamo rilevato un contorno che non è altro che una linea retta, ovvero il bordo del coprivetrino
NANOGPS_AREA = 10000000 #il NanoGPS viene fissato al vetrino con dello scotch, che andrà a prendere un area molto vasta del vetrino, sicuramente almeno magggiore di questa soglia
MICRONx_x5 = 960
MICRONy_x5 = 810
PIXEL_IMG_x = 428
PIXEL_IMG_y = 360

class GlassType(Enum):
    TWO_COLORED = 0
    TWO_WHITE = 1
    ONE_COLORED = 2
    ONE_WHITE = 3
    ONE_BOTH = 4
    EMPTY = 5

def slide_analisys(path_img):

    conn = mysql.connector.connect(
        host="localhost",      
        user="root",
        password="Giocondo2021$",
        database="Raman_DB"
    )

    cursor = conn.cursor()

    glass = GlassType.EMPTY
    img = cv2.imread(path_img, cv2.IMREAD_COLOR)
    if img is None:
        return -1
    
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #applico bitmap e un po di filtri per definire meglio i contorni
    _, bitmapImg = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY_INV)
    bitmapImg = cv2.blur(bitmapImg, (17,17))
    bitmapImg = cv2.bilateralFilter(bitmapImg, 30, 75, 75)  #img, pixel considerati, considerazione diverse intensità di colore, considerare distanza
    
    #ricerca dei contorni
    contours, _ = cv2.findContours(bitmapImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    nanoGPS = False
    xNano = yNano = wNano = hNano = None
    contoursNoNanoGPS= []
    print(len(contours))
    #filtro i contorni andando a cercare prima di tutto il NanoGPS se presente, che avra una forma rettangolare
    #dopo controllo le dimensioni dei contorni trovati di dimensione rilevante che saranno i campioni, escludendo 
    #quelli con dimensione troppo elevata che corrisponderanno alle linee del vetrino
    for i in contours:

        perimeter = cv2.arcLength(i, closed=True)
        area = cv2.contourArea(i)
        comp = area / (perimeter * perimeter)

        #if comp < LINE_BOUND: #soglia bassa che indica che abbiamo rilevato le linee del coprivetrino
            #continue
        #elif len(approx)== 4 and cv2.isContourConvex(approx) and not nanoGPS and area > NANOGPS_AREA:
            #nanoGPS = True
            #(xNano,yNano,wNano,hNano) = cv2.boundingRect(approx)
        #else:
        contoursNoNanoGPS.append(i)
    
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, contoursNoNanoGPS, -1, 255, 5)
    cv2.imwrite("prova.jpg", mask)
    #plt.figure(figsize=[15,8])
    #plt.subplot(); plt.axis('on'); plt.imshow(mask, cmap="gray"); plt.title("Not colored")
    #plt.show()
    largest_contour = max(contoursNoNanoGPS, key=cv2.contourArea)
    largestArea = cv2.contourArea(largest_contour)
    
    filter_contours_gray = []
    for i in contoursNoNanoGPS:
        area = cv2.contourArea(i)
        if area > largestArea * 0.75 and area < largestArea * 1.25: #se ci sono 2 figure con aree simili saranno 2 campioni invece che uno solo
            filter_contours_gray.append(i)

    #mask = np.zeros(img.shape[:2], dtype=np.uint8)
    #cv2.drawContours(mask, contoursNoNanoGPS, -1, 255, 5)
    #cv2.imwrite("prova.jpg", mask)
    #plt.figure(figsize=[15,8])
    #plt.subplot(); plt.axis('on'); plt.imshow(prova, cmap="gray"); plt.title("Not colored")
    #plt.show()
    
    if not nanoGPS:
        print("NanoGPS non presente")
    else:
        print("NanoGPS presente")

    #creo una maschera con i contorni della figuara con la quale controllo se all'interno il colore medio
    #e il viola, e quindi è un campione colorato oppure no
    colored = []
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    for i in filter_contours_gray:
        cv2.drawContours(mask, [i], -1, 255, thickness=cv2.FILLED)
        mean_color = cv2.mean(img, mask=mask)
        mean_color_bgr = np.array(mean_color[:3], dtype=np.uint8).reshape(1,1,3)
        mean_color_hsv = cv2.cvtColor(mean_color_bgr, cv2.COLOR_BGR2HSV)[0,0]
        hue = mean_color_hsv[0] 
        print(hue)
        
        light_purple = 90
        dark_purple = 140
        if hue > light_purple and hue <dark_purple:
            colored.append(i)
            print("pattern colorato")

    if len(colored)>0: 
      
        if len(colored)==2:
            glass = GlassType.TWO_COLORED
        elif len(colored)==1:
            glass = GlassType.ONE_COLORED

    left = False
    
    filter_contours_gray = sorted(filter_contours_gray, key=lambda c: cv2.boundingRect(c)[0])
    #in base ai risultati definisco il tipo di vetrino che ho trovato
    if len(filter_contours_gray) == 2 and glass == GlassType.ONE_COLORED:
        glass = GlassType.ONE_BOTH
        x_min1 = filter_contours_gray[0][:, 0, 0].min()
        x_min2 = filter_contours_gray[1][:, 0, 0].min()
        if (x_min1 - colored[0][:, 0, 0].min()) < (x_min2 - colored[0][:, 0, 0].min()):
            left = True
    elif len(filter_contours_gray) == 2 and glass==GlassType.EMPTY:
        glass = GlassType.TWO_WHITE
    elif len(filter_contours_gray) == 1 and glass==GlassType.EMPTY:
        glass = GlassType.ONE_WHITE
    elif len(filter_contours_gray) > 2:
        print("Errore nella rilevazione dei contorni, rumore troppo elevato")
        return -1
    elif len(filter_contours_gray) == 0:
        print("Vetrino vuoto o campione troppo frammentato")
        return 0 

    contour_img = np.zeros(img_gray.shape, dtype=np.uint8)
    approx_contours = []
    centr = []
    for idx in range(len(filter_contours_gray)):
        approx_contours.append(cv2.approxPolyDP(filter_contours_gray[idx], 5, True))
        centr.append(compute_center([approx_contours[idx]]))
    
    contour_img = cv2.drawContours(contour_img, filter_contours_gray, -1, 255, -1)
    
    final_img = [[] for _ in filter_contours_gray]
    idx = 0
    for i in filter_contours_gray:
        final_img[idx] = np.zeros(img_gray.shape, dtype=np.uint8)
        final_img[idx] = cv2.drawContours(final_img[idx], [i], -1, 255, -1)
        idx += 1
    #plt.figure(figsize=[15,8])
    #plt.subplot(); plt.axis('on'); plt.imshow(img, cmap="gray"); plt.title("Not colored")
    #plt.show()
    
    # ottengo il path relativo da usare come chiave primaria in DB, non controllo che sia nella directory dell'App 
    # perché questo controllo è già fatto nell'applicazione principale al momento del caricamento del vetrino
    relative_path = os.path.relpath(path_img, os.getcwd()) 
    print(relative_path)
    basename = os.path.basename(path_img)
    
    #salvo le immagini dei contorni da usare poi per il matching con computeDistance
    name = os.path.splitext(basename)[0] + "_contour.jpg"
    new_path = os.path.join(os.path.dirname(relative_path), name) 
    cv2.imwrite(new_path, contour_img)

    if nanoGPS:
            cursor.execute("""
                INSERT INTO Slide(Filepath, NanoGPS, x_nano, y_nano, ContourPath)
                        VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE NanoGPS = VALUES(NanoGPS), x_nano = VALUES(x_nano), y_nano = VALUES(y_nano), ContourPath = VALUES(ContourPath)
                       """, (relative_path, nanoGPS, float(xNano), float(yNano), new_path))
    else: 
        cursor.execute("""
            INSERT INTO Slide(Filepath, NanoGPS, ContourPath)
                    VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE NanoGPS = VALUES(NanoGPS), ContourPath = VALUES(ContourPath)
                       """, (relative_path, nanoGPS, new_path))

    cursor.execute("""
                DELETE FROM Pattern WHERE Slide = %s
                       """, (relative_path,))
    
    dir = os.path.join(os.path.dirname(relative_path), "Raman_Acquisition")
    os.makedirs(dir, exist_ok=True)
    
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
            if idx==0 and left:
                colored = True
            elif idx==1 and not left:
                colored = True
        print("inserisco")

        patternImg = img[y_min:y_max, x_min:x_max]
        name = os.path.splitext(basename)[0] + "_pattern" + str(idx) + ".jpg"
        pattern_path = os.path.join(os.path.dirname(relative_path), name)
        cv2.imwrite(pattern_path, patternImg)
        print(x_min)
        offset_x_min = x_min - (x_min % PIXEL_IMG_x)
        offset_y_min = y_min - (y_min % PIXEL_IMG_y)
        offset_x_max = x_max - (x_max % PIXEL_IMG_x) + PIXEL_IMG_x
        offset_y_max = y_max - (y_max % PIXEL_IMG_y) + PIXEL_IMG_y
        num_row = (offset_x_max - offset_x_min) // PIXEL_IMG_x
        num_col = (offset_y_max - offset_y_min) // PIXEL_IMG_y
        jsonTree = {}
        for i in range(num_row):
            start_x = int(offset_x_min + (i * PIXEL_IMG_x)) 
            for j in range(num_col):
                start_y = int(offset_y_min + (j * PIXEL_IMG_y)) 
                dir = os.path.join(os.path.dirname(relative_path), f"{start_x*MICRONx_x5//PIXEL_IMG_x}_{start_y*MICRONy_x5//PIXEL_IMG_y}")
                if os.path.exists(dir):
                    shutil.rmtree(dir) 
                os.makedirs(dir)
                jsonImg = img[start_y:start_y+PIXEL_IMG_y, start_x:start_x+PIXEL_IMG_x] 
                name = f"{start_x*MICRONx_x5//PIXEL_IMG_x}_{start_y*MICRONy_x5//PIXEL_IMG_y}.jpg"
                pattern_path = os.path.join(dir, name)
                cv2.imwrite(pattern_path, jsonImg)
                jsonTree[f"{start_x *MICRONx_x5//PIXEL_IMG_x}_{start_y *MICRONy_x5//PIXEL_IMG_y}"] = {"path":pattern_path, "child":[], "acquired":False}
        x_min = x_min * MICRONx_x5 // PIXEL_IMG_x #+ MICRONx_x5//2
        y_min = y_min * MICRONy_x5 // PIXEL_IMG_y #+ MICRONy_x5//2
        y_max = y_max * MICRONy_x5 // PIXEL_IMG_y #+ MICRONy_x5//2
        x_max = x_max * MICRONx_x5 // PIXEL_IMG_x #+ MICRONx_x5//2
        cursor.execute("""
            INSERT INTO Pattern(Slide, x_min, y_min, x_max, y_max, x_centr, y_centr, Colored, images_tree)
                    VALUES ( %s,  %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (relative_path, float(x_min), float(y_min), float(x_max), float(y_max), float(center[0]), float(center[1]), colored, json.dumps(jsonTree)))

    conn.commit()
    cursor.close()
    conn.close()

    #plt.figure(figsize=[15,8])
    #plt.subplot(121); plt.axis('on'); plt.imshow(final_img[0], cmap="gray"); plt.title("Not colored")
    #plt.subplot(122); plt.axis('on'); plt.imshow(final_img[1], cmap="gray"); plt.title("Colored")
    #plt.show()
    
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