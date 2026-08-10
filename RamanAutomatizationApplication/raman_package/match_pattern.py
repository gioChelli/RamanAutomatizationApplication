import cv2
import numpy as np
import matplotlib.pyplot as plt
import concurrent.futures
import math
import os

#def search_distance_hull(final_contours, final_img):

    #hull1 = cv2.convexHull(final_contours[0][0])
    #hull2 = cv2.convexHull(final_contours[1][0])

    #centr1 = compute_center([hull1])
    #centr2 = compute_center([hull2])

    #hull2 = hull2 - centr2 + centr1

    #resBest = -1
    #bestRot = 0
    #haus = cv2.createShapeContextDistanceExtractor()  #createShapeContextDistanceExtractor
    #center = tuple(map(int, centr1))
    #for i in range(360):
        
        #rotMatrix = cv2.getRotationMatrix2D(center, i, 1.0)
        #rotated_contours = cv2.transform(hull2, rotMatrix)
        
        #distance = haus.computeDistance(hull1, rotated_contours)
        
        #if(resBest == -1 or distance < resBest):
            #resBest = distance
            #bestRot = i
        #print(i, distance)

    #print(bestRot)

    #rotMatrix = cv2.getRotationMatrix2D(center, bestRot, 1.0)
    #rotated_contours = cv2.transform(hull2, rotMatrix)

    #img = np.zeros(final_img[0].shape, dtype=np.uint8)
    #img = cv2.drawContours(img, [hull1], -1, 255, 7)
    #img = cv2.drawContours(img, [rotated_contours], -1, 255, 7)

    #plt.figure(figsize=[15,8])
    #plt.subplot(); plt.axis('on'); plt.imshow(img, cmap="gray"); plt.title("Not colored")
    #plt.show()

    #return bestRot

def search_contours(img, patt):
    
    _, bitmapImg = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(bitmapImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)
    largestArea = cv2.contourArea(largest_contour)
    filter_contours = []
    for i in contours:
        area = cv2.contourArea(i)
        if area > largestArea * 0.75 and area < largestArea * 1.25: #se ci sono 2 figure con aree simili saranno 2 campioni invece che uno solo
            filter_contours.append(i)

    print(len(filter_contours))
    if len(filter_contours) == 2:
        contours = sorted(filter_contours, key=lambda c: cv2.boundingRect(c)[0])
        if patt == "A":
            contours = [contours[0]]
        else:
            contours = [contours[1]]
    elif len(contours) >2 or len(contours)<1:
        return -1
    
    return contours

def search_center(contour):
    M1 = cv2.moments(contour)
    if M1["m00"] == 0:
        return -1
    cx = int(M1["m10"] / M1["m00"])  # coordinata X del centro
    cy = int(M1["m01"] / M1["m00"])  # coordinata Y del centro

    return (cx, cy)


def match_pattern(path_img1, path_img2, patt1, patt2):
    print(patt1, patt2)
    print(path_img1)

    absFilpath1 = os.path.join(os.getcwd(), path_img1)
    absFilpath2 = os.path.join(os.getcwd(), path_img2)

    img1 = cv2.imread(absFilpath1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(absFilpath2, cv2.IMREAD_GRAYSCALE)
    if img1 is None or img2 is None:
        return -1

    contours1 = search_contours(img1, patt1)
    contours2 = search_contours(img2, patt2)

    center1 = search_center(contours1[0])
    center2 = search_center(contours2[0])

    height, width = img1.shape
    bestRot = None
    resBest =  float("inf")
    iou = 0
    rotIoU = None

    approx_contours1 = cv2.approxPolyDP(contours1[0], 2, True)
    approx_contours2 =  cv2.approxPolyDP(contours2[0], 2, True)
    shift = (np.array(center1) - np.array(center2)).astype(np.int32)
    approx_contours2 = approx_contours2 + shift

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i in range(360):
            futures.append(executor.submit(search_distance, i, approx_contours1, approx_contours2, center1, width, height))
        
        for future in futures:
            risultato = future.result()  
            if math.isnan(risultato[0]):
                continue
            if resBest ==  float("inf") or risultato[0] < resBest:
                resBest = risultato[0]
                bestRot = risultato[1]
            if risultato[2] > iou:
                iou = risultato[2]
                rotIoU = risultato[1]
        
        j = 0.1
        futures = []
        while j < 1:
            futures.append(executor.submit(search_distance, bestRot + j, approx_contours1, approx_contours2, center1, width, height))
            futures.append(executor.submit(search_distance, bestRot - j, approx_contours1, approx_contours2, center1, width, height))
            j += 0.1
         
        for future in futures:
            risultato = future.result()
            if risultato[0] < resBest:
                resBest = risultato[0]
                bestRot = risultato[1]  
            if risultato[2] > iou:
                iou = risultato[2]
                rotIoU = risultato[1]
    
    print(f"Risultato migliore: {resBest}, Rotazione: {bestRot}" )
    print(f"IoU ottimo: {iou}, Rotazione IoU: {rotIoU}" )
    #bestRot = 198.9
    
    return 0, bestRot, center1[0], center1[1], center2[0], center2[1], contours1[0], contours2[0], width, height, rotIoU

    
def search_distance(rot, contour1, contour2, centr1, width, height):
    sc = cv2.createShapeContextDistanceExtractor()
    rotMatrix = cv2.getRotationMatrix2D(centr1, -rot, 1.0)
    rotated_contours = cv2.transform(contour2, rotMatrix)
        
    try:
        distance = sc.computeDistance(contour1, rotated_contours)
    except cv2.error as e:
        distance = float("inf")
    print(rot, distance)

    #calcolo intersection over union
    mask1 = np.zeros((height, width), dtype=np.uint8)
    mask2 = np.zeros((height, width), dtype=np.uint8)

    cv2.drawContours(mask1, [contour1], -1, 255, -1)
    cv2.drawContours(mask2, [rotated_contours], -1, 255, -1)

    intersection = cv2.bitwise_and(mask1, mask2)
    union = cv2.bitwise_or(mask1, mask2)

    iou = np.sum(intersection > 0) / np.sum(union > 0)
    print("IoU:", iou)

    
    return distance, rot, iou

#fine calcolo
    #rotMatrix = cv2.getRotationMatrix2D(centr1, bestRot, 1.0)
    #rotated_contours = cv2.transform(contour2[0], rotMatrix)

    #img = np.zeros((height, width), dtype=np.uint8)
    #img = cv2.drawContours(img, [approx_contours1], -1, 255, 7)
    #img = cv2.drawContours(img, [rotated_contours], -1, 255, 7)

    #plt.figure(figsize=[15,8])
    #plt.axis('on'); plt.imshow(img, cmap="gray"); plt.title("Not colored")
    #plt.show()