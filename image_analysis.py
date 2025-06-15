from enum import Enum
import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys
import os
from scipy.spatial.distance import cdist

WHITE_COLOR = 255
#qusti sono tutti valori che rappresentano i pixel
PATTERN_MIN_DIMENSION = 10000  #potenziale problema del codice, potrei scegliere di fare un ciclo fino a che non rimango con 1 o 2 oggetti
PATTERN_FRAGMENT_MIN_DIMENSION = 1000 #dimensione minima dei frammenti che ci interessano, tutto cio che e piu piccolo puo essere polvere o comunque come affermato dagli istologi irrilevante
FRAGMENT_MAX_DISTANCE = 100 #campo che prendo in considerazione intorno a un pattern, in cui ci potrebbero essere frammenti interessanti

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

    #ottengo la maschera per individuare vetrini colorati
    result = onlyPurple(img) 
    result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    
    #controllo se c'è campione colorato
    if not np.mean(result) >= WHITE_COLOR: 
        
        #se e presente un campione colorato vado a vedere i contorni per trovare se ne ho 2 oppure 1
        _, bitmapImg = cv2.threshold(result, 127, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(bitmapImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filter_contours = []
        for i in contours:
            if len(i) > PATTERN_MIN_DIMENSION:
                filter_contours.append(i)
        if len(filter_contours)==2:
            glass = GlassType.TWO_COLORED
        elif len(filter_contours)==1:
            glass = GlassType.ONE_COLORED
        elif len(filter_contours) > 2:
            print("Errore nella rilevazione degli oggetti")
            return -1

    result = None
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #applico bitmap e un po di filtri per definire meglio i contorni
    _, bitmapImg = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    bitmapImg = cv2.blur(bitmapImg, (13,13)) #applico filtro per sfocatura su un campo di 13 pixel
    bitmapImg = cv2.bilateralFilter(bitmapImg, 30, 75, 75)  #img, pixel considerati, considerazione diverse intensità di colore, considerare distanza
    #ricerca dei contorni
    contours, _ = cv2.findContours(bitmapImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    img = None
    nanoGPS = []
    filter_contours = []

    #filtro i contorni andando a cercare prima di tutto il NanoGPS se presente, che avra una forma rettangolare
    #dopo controllo le dimensioni dei contorni trovati di dimensione rilevante che saranno i campioni, escludendo 
    #quelli con dimensione troppo elevata che corrisponderanno alle linee del vetrino
    for i in contours:
        epsilon = 0.02 * cv2.arcLength(i, True)
        approx = cv2.approxPolyDP(i, epsilon, True)
        if len(approx)== 4 and cv2.isContourConvex(approx) and len(nanoGPS) == 0:
            nanoGPS = approx
            (x2,y2,w2,h2) = cv2.boundingRect(approx)
            idx = i
        elif len(approx)== 4 and cv2.isContourConvex(approx):
            (x1,y1,w1,h1) = cv2.boundingRect(approx)
            if (w1 * h1) > (w2 * h2):
                nanoGPS = approx
                (x2, y2, w2, h2) = (x1,y1,w1, h1) #qui ho le coordinate del NanoGPS che poi posso usare come riferimento
        elif(len(i) > PATTERN_MIN_DIMENSION and len(i) < (bitmapImg.shape[1])):
            filter_contours.append(approx)
    
    #in base ai risultati definisco il tipo di vetrino che ho trovato
    if len(filter_contours) == 2 and glass == "ONE COLORED":
        glass = GlassType.ONE_BOTH
    elif len(filter_contours) == 2 and glass == "EMPTY":
        glass = GlassType.TWO_WHITE
    elif len(filter_contours) == 1 and glass == "EMPTY":
        glass = GlassType.ONE_WHITE
    elif len(filter_contours) > 2:
        print("Errore nella rilevazione dei contorni")
        return -1
    elif len(filter_contours) == 0:
        print("Vetrino vuoto o campione troppo frammentato")
        return 0 

    #aggiungo ai contorni dei campioni(ovvero quelli piu grandi) altri contorni a loro vicini che potrebbero
    #sempre fare parte del campione ma essere leggermente staccati per via del talgio oppure fattori di rumore
    final_contours = [[] for _ in filter_contours]
    for i in contours:
        idx = 0
        for j in filter_contours:
            if contour_distance(i, j) < FRAGMENT_MAX_DISTANCE and len(i) > PATTERN_FRAGMENT_MIN_DIMENSION:
                final_contours[idx].append(i)
                break
            idx += 1
    
    #parte per vedere i risultati
    final_img = [[] for _ in final_contours]
    centr = [[] for _ in final_contours]
    idx = 0
    for i in final_contours:

        final_img[idx] = np.zeros(bitmapImg.shape, dtype=np.uint8)
        final_img[idx] = cv2.drawContours(final_img[idx], i, -1, 255, 15)
        coords = cv2.findNonZero(final_img[idx])
        x_min = coords[:, 0, 0].min()
        y_min = coords[:, 0, 1].min()
        x_max = coords[:, 0, 0].max()
        y_max = coords[:, 0, 1].max()
        #qua codice ottimizzabile
        y1 = max(y_min - 100, 0)
        y2 = min(y_max + 100, final_img[idx].shape[0])
        x1 = max(x_min - 100, 0)
        x2 = min(x_max + 100, final_img[idx].shape[1])

        final_img[idx] = final_img[idx][y1:y2, x1:x2]
        centr[idx] = compute_center(i)
        #final_img[idx] = cv2.circle(final_img[idx], centr[idx], radius=30, color=255, thickness=-1)
        idx += 1

    bitmapImg = None
    
    bestRot = 0
    i = 0
    sc = cv2.createShapeContextDistanceExtractor()
    while i < 360:
        
        centr = compute_center([filter_contours[1]])
        centr = tuple(map(int, centr))
        rotMatrix = cv2.getRotationMatrix2D(centr, i, 1.0)
        rotated_contours = cv2.transform(filter_contours[1], rotMatrix)
        
        distance = sc.computeDistance(filter_contours[0], rotated_contours)
        
        if(distance < resBest):
            resBest = distance
            bestRot = i
        print(i, distance)
        i = i + 1

    img1 = np.zeros(img1.shape, dtype=np.uint8)
    img2 = np.zeros(img2.shape, dtype=np.uint8) 
    cv2.drawContours(img1, filter_contours[0], -1, 255, 3)
    cv2.drawContours(img1, filter_contours[1], -1, 255, 3)

    #cv2.circle(img1, (cx1, cy1), radius=30, color=255, thickness=-1)
    #cv2.circle(img2, (cx2, cy2), radius=30, color=255, thickness=-1)

    plt.figure(figsize=[15,8])
    plt.subplot(121); plt.axis('on'); plt.imshow(final_img[0], cmap="gray"); plt.title("Not colored")
    plt.subplot(122); plt.axis('on'); plt.imshow(final_img[1], cmap="gray"); plt.title("Colored")
    plt.show()

    if len(final_img) == 2:
        match_SIFT(final_img)
    
    #cv2.imwrite("SIFT_result.jpg", img3)
    #cv2.imwrite("ORB_result.jpg", img4)

    print(glass)
    return 0

def match_ORB(final_img):
    kpORB = [[] for _ in final_img]
    desORB = [[] for _ in final_img]

    idx = 0
    for i in final_img: 
        kpORB[idx], desORB[idx] = compute_ORB_keypoints(i)
        idx += 1

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches2 = bf.match(desORB[0],desORB[1])

    matches2 = sorted(matches2, key = lambda x:x.distance)
    img4 = cv2.drawMatches(final_img[0],kpORB[0],final_img[1],kpORB[1],matches2[:10],None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

    plt.imshow(img4),plt.show()
    
def match_SIFT(final_img):
    kpSIFT = [[] for _ in final_img]
    desSIFT = [[] for _ in final_img]

    idx = 0
    for i in final_img: 
        kpSIFT[idx], desSIFT[idx] = compute_SIFT_keypoints(i)
        idx += 1

    bf = cv2.BFMatcher()
    matches1 = bf.knnMatch(desSIFT[0],desSIFT[1],k=2)

    good = []
    for m,n in matches1:
        if m.distance < 0.85 * n.distance:
            good.append([m])

    img3 = cv2.drawMatchesKnn(final_img[0],kpSIFT[0],final_img[1],kpSIFT[1],good[:50],None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    plt.imshow(img3),plt.show()

def match_AKAZE(final_img):
    kpAKAZE = [[] for _ in final_img]
    desAKAZE = [[] for _ in final_img]

    idx = 0
    for i in final_img: 
        kpAKAZE[idx], desAKAZE[idx] = compute_AKAZE_keypoints(i)
        idx += 1

    #bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    #matches = bf.match(desAKAZE[0], desAKAZE[1])
    #matches = sorted(matches, key=lambda x: x.distance)
    #img5 = cv2.drawMatches(final_img[0], kpAKAZE[0], final_img[1], kpAKAZE[1], matches[:20], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    #media_distanza = sum(m.distance for m in matches[:20]) / 20
    
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    raw_matches = bf.knnMatch(desAKAZE[0], desAKAZE[1], k=2)

    # Lowe's ratio test
    good = []
    for m, n in raw_matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)

    # Ora puoi usare good[:20]
    img_matches = cv2.drawMatches(final_img[0], kpAKAZE[0], final_img[1], kpAKAZE[1], good[:20], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    plt.imshow(img_matches), plt.show()

    #plt.imshow(img5),plt.show()
    

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

def compute_SIFT_keypoints(img):
    sift = cv2.SIFT_create()
    kp, des = sift.detectAndCompute(img,None)
    return kp, des

def compute_ORB_keypoints(img):
    orb = cv2.ORB_create()
    kp, des = orb.detectAndCompute(img,None)
    return kp, des

def compute_AKAZE_keypoints(img):
    akaze = cv2.AKAZE_create()
    kp, des = akaze.detectAndCompute(img, None)
    return kp, des

if len(sys.argv) == 2:
    main(sys.argv[1])
else:
    print("Uso:", sys.argv[0], "nome_directory")