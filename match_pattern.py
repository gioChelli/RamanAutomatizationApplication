import cv2
import numpy as np
import sys
import matplotlib.pyplot as plt
import json

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
    contours, _ = cv2.findContours(bitmapImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if len(contours) == 2:
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])
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


def main(path_img1, path_img2, patt1, patt2):
    
    img1 = cv2.imread(path_img1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(path_img2, cv2.IMREAD_GRAYSCALE)
    if img1 is None or img2 is None:
        return -1
    
    contours1 = search_contours(img1, patt1)
    contours2 = search_contours(img2, patt2)

    center1 = search_center(contours1[0])
    center2 = search_center(contours2[0])

    height, width = img1.shape

    bestRot = search_distance(contours1, contours2, center1, center2, width, height)

    print(bestRot)
    print(center1[0])
    print(center1[1])
    print(center2[0])
    print(center2[1])
    print(json.dumps(contours1[0].tolist()))
    print(json.dumps(contours2[0].tolist()))
    print(width)
    print(height)

    return 0

    
def search_distance(contour1, contour2, centr1, centr2, width, height):

    approx_contours1 = cv2.approxPolyDP(contour1[0], 3, True)
    approx_contours2 =  cv2.approxPolyDP(contour2[0], 3, True)
    shift = (np.array(centr1) - np.array(centr2)).astype(np.int32)
    approx_contours2 = approx_contours2 + shift

    resBest = -1
    bestRot = 0
    sc = cv2.createShapeContextDistanceExtractor()  #createShapeContextDistanceExtractor
    
    for i in range(360):
        
        rotMatrix = cv2.getRotationMatrix2D(centr1, i, 1.0)
        rotated_contours = cv2.transform(approx_contours2, rotMatrix)
        
        distance = sc.computeDistance(approx_contours1, rotated_contours)
        
        if(resBest == -1 or distance < resBest):
            resBest = distance
            bestRot = i
        #print(i, distance)

    rotMatrix = cv2.getRotationMatrix2D(centr1, bestRot, 1.0)
    rotated_contours = cv2.transform(contour2[0], rotMatrix)

    img = np.zeros((height, width), dtype=np.uint8)
    img = cv2.drawContours(img, [approx_contours1], -1, 255, 7)
    img = cv2.drawContours(img, [rotated_contours], -1, 255, 7)

    #plt.figure(figsize=[15,8])
    #plt.axis('on'); plt.imshow(img, cmap="gray"); plt.title("Not colored")
    #plt.show()

    return bestRot

if __name__ == "__main__":
    
    if len(sys.argv) == 5:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])