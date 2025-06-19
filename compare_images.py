from enum import Enum
import numpy as np
import cv2
import matplotlib.pyplot as plt
import sys
from scipy.spatial.distance import cdist

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


def main(paths_imgs):
    img1 = cv2.imread(paths_imgs[0], cv2.IMREAD_COLOR)
    img2 = cv2.imread(paths_imgs[1], cv2.IMREAD_COLOR)
    if img1 is None or img2 is None:
        return -1
    
    match_AKAZE(img1, img2)

if len(sys.argv) == 3:
    main([sys.argv[1], sys.argv[2]])
else:
    print("Uso:", sys.argv[0], "prima_immagine", "seconda_immagine")