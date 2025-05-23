import cv2
import numpy as np
import matplotlib.pyplot as plt

def main():

    #kernel = (3,3)
    kernel1 = np.ones((3, 3), np.uint8)

    img1_name = "acqBianco2_unita.jpg"  # iperparametro da passare quando ho diversi vetrini
    img2_name = "acqColorato1_unita.jpg"    # iperparametro da passare quando ho diversi vetrini
    
    img1 = cv2.imread(img1_name, cv2.IMREAD_COLOR)
    img2 = cv2.imread(img2_name, cv2.IMREAD_COLOR)
    result = onlyPurple(img2)

    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)    
    img2_gray = cv2.cvtColor(result, cv2.COLOR_HSV2BGR) 
    img2_gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY) 

    matrix1 = np.ones(img2_gray.shape, dtype="uint8") * 70 #matrice usata per schiarire rimuovere rumore
    matrix3 = np.ones(img2_gray.shape) * 1.3 #per +  contrasto
    
    img1_gray = cv2.add(img1_gray, matrix1)  #schiarisco la figura non colorata perche piu scura e con maggior rumore
    img2_gray = np.uint8(np.clip(cv2.multiply(np.float64(img2_gray), matrix3), 0, 255))
    img1_gray = np.uint8(np.clip(cv2.multiply(np.float64(img1_gray), matrix3), 0, 255))

    img1_gray = cv2.adaptiveThreshold(img1_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 3) #bitmap adattiva
    img2_gray = cv2.adaptiveThreshold(img2_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 13, 3)

    img1_gray = cv2.bilateralFilter(img1_gray, 30, 75, 75)  #filtro dove elimino un po di rumore e delimitare i contorni
    img2_gray = cv2.bilateralFilter(img2_gray, 30, 75, 75) 

    density = cv2.blur(img2_gray.astype(np.float32), (11, 11)) / 255
    mask = (density > 0.000005).astype(np.uint8) * 255
    new_img2 = np.maximum(img2_gray, mask.astype(np.uint8))

    #plt.figure(figsize=[15,8])
    #plt.subplot(121); plt.axis('on'); plt.imshow(img1_gray, cmap="gray"); plt.title("Not colored")
    #plt.subplot(122); plt.axis('on'); plt.imshow(new_img2, cmap="gray"); plt.title("Colored")
    
    #plt.show()
        
    contours, _ = cv2.findContours(img1_gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)    #coi parametri indico di non approssimare
    contours2, _ = cv2.findContours(new_img2, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    img1 = np.zeros(img1_gray.shape, dtype=np.uint8)
    img2 = np.zeros(img2_gray.shape, dtype=np.uint8)

    cv2.drawContours(img1, contours, -1, 255, 3)
    cv2.drawContours(img2, contours2, -1, 255, 3)

    # Rimuove piccoli oggetti bianchi isolati
    cleaned1 = cv2.morphologyEx(img1, cv2.MORPH_CLOSE, kernel1)
    cleaned2 = cv2.morphologyEx(img2, cv2.MORPH_CLOSE, kernel1)

    contours1, _ = cv2.findContours(cleaned1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours2, _ = cv2.findContours(cleaned2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    filter_contours1 = []
    for i in contours1:
        if(len(i) > 10000):
            filter_contours1.append(i)

    filter_contours2 = []
    for i in contours2:
        if(len(i) > 3000):
            filter_contours2.append(i)

    img1 = np.zeros(img1.shape, dtype=np.uint8)
    img2 = np.zeros(img2.shape, dtype=np.uint8)

    cv2.drawContours(img1, filter_contours1, -1, 255, 3)
    cv2.drawContours(img2, filter_contours2, -1, 255, 3)
    
    square1 = 0
    square2 = 0
    m10 = 0
    m01 = 0
    i = 0
    for c in filter_contours1:
        M1 = cv2.moments(c)
        square1 += M1["m00"]
        m10 += max(m10, M1["m10"])
        m01 += max(m01, M1["m01"])
        i += 1

    square1 = square1 / i
    m10 = m10 / i
    m01 = m01 / i

    cx1 = int(m10 / square1)  # coordinata X del centro
    cy1 = int(m01 / square1)  # coordinata Y del centro
    
    m10 = 0
    m01 = 0
    i = 0
    for c in filter_contours2:
        M2 = cv2.moments(c)
        square2 += M2["m00"]
        m10 = max(m10, M2["m10"])
        m01 += max(m01, M2["m01"])
        i += 1
        
    cx2 = int(m10 / square2)  # coordinata X del centro
    cy2 = int(m01 / square2)  # coordinata Y del centro

    print(cx1, cx2)
    print(cy1, cy2)
    print(square1)
    print(square2)

    cv2.circle(img1, (cx1, cy1), radius=30, color=255, thickness=-1)
    cv2.circle(img2, (cx2, cy2), radius=30, color=255, thickness=-1)

    i = 0
    resTot = 0
    resBest = 1

    while i < 90:
         
        counter = 0
        for f in filter_contours2:
            resTot +=  cv2.matchShapes(filter_contours1[0], f, cv2.CONTOURS_MATCH_I1, 0.0) 
            counter += 1
        resTot = resTot / counter

        if(resTot < resBest):
            resBest = resTot
            img2 = np.zeros(img2.shape, dtype=np.uint8)
            for f in filter_contours2:
                cv2.drawContours(img2, f, -1, 255, 3)
            print(i)

        for f in filter_contours2:
            rotMatrix = cv2.getRotationMatrix2D((cx2, cy2), i, 1.0)
            f = cv2.transform(f, rotMatrix)
        i = i + 1

    print(resBest)
    
    plt.figure(figsize=[15,8])
    plt.subplot(121); plt.axis('on'); plt.imshow(img1, cmap="gray"); plt.title("Not colored")
    plt.subplot(122); plt.axis('on'); plt.imshow(img2, cmap="gray"); plt.title("Colored")
    
    plt.show()

    return

def onlyPurple(img2):

    hsv = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
    lower_purple = np.array([125, 5, 5], dtype=np.uint8)
    upper_purple = np.array([160, 255, 255], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower_purple, upper_purple)

    # Crea immagine bianca  
    white_background = np.full(img2.shape, 255, dtype=np.uint8)
    purple_background = np.full(img2.shape,  np.array([140, 80, 80], dtype=np.uint8), dtype=np.uint8)

    # Applica maschera: dove è True, mantieni il colore viola, altrimenti bianco
    result = np.where(mask[:, :, np.newaxis] == 255, purple_background, white_background)

    #plt.figure(figsize=[15,8])
    #plt.imshow(result); plt.title("Colored")
    
    #plt.show()

    return result

main()