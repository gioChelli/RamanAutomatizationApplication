import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

MAX_NUM_FEATURES = 500

def main():

    img1_name = "acqBianco_unita.jpg"    # iperparametro da passare quando ho diversi vetrini
    img2_name = "acqColorato_unita.jpg"  # iperparametro da passare quando ho diversi vetrini

    img1 = cv2.imread(img1_name, cv2.IMREAD_COLOR)
    img2 = cv2.imread(img2_name, cv2.IMREAD_COLOR)

    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)    
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY) 

    matrix = np.ones(img2_gray.shape, dtype="uint8") * 70

    img1_gray = cv2.add(img1_gray, matrix)
    img2_gray = cv2.subtract(img2_gray, matrix)

    img1_gray = cv2.adaptiveThreshold(img1_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 5)
    img2_gray = cv2.adaptiveThreshold(img2_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 7)

    plt.figure(figsize=[20,10])

    plt.subplot(121); plt.axis('on'); plt.imshow(img1_gray, cmap="gray"); plt.title("Original Form")
    plt.subplot(122); plt.axis('on'); plt.imshow(img2_gray, cmap="gray"); plt.title("Scanned Form")
    
    
    plt.show()

    return

main()